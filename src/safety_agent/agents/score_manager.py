"""
Score Manager Agent - Scores hazards using risk matrices.

Responsibilities:
- Calculate severity, likelihood, RPN for each hazard using LLM
- Adjust likelihood based on historical incident data
- Compute culture score delta
- Assign priority and due dates based on SLA
"""

import logging
from datetime import datetime, timedelta

from safety_agent.agents.base import BaseAgent, AgentError
from safety_agent.llm.client import LLMClient
from safety_agent.schemas import Hazard, ScoredHazard, Priority
from safety_agent.tools.risk_matrix import RiskMatrixPolicy
from safety_agent.tools.incident_history import IncidentHistoryDB
from safety_agent.tools.metrics_db import MetricsDB

logger = logging.getLogger(__name__)


class ScoreManagerAgent(BaseAgent[list[Hazard], list[ScoredHazard]]):
    """
    Agent that scores hazards using LLM-based risk assessment.

    Uses LLM to:
    - Assess severity based on potential consequences
    - Evaluate base likelihood considering the context

    Uses tools:
    - RiskMatrixPolicy: Lookup RPN and priority from scores
    - IncidentHistoryDB: Adjust likelihood based on past incidents
    - MetricsDB: Update and track culture scores

    Input: list[Hazard]
    Output: list[ScoredHazard]
    """

    name = "ScoreManagerAgent"

    # SLA definitions: priority -> days until due
    PRIORITY_SLA_DAYS = {
        Priority.CRITICAL: 0,   # Same day
        Priority.HIGH: 1,       # Next day
        Priority.MEDIUM: 7,     # Within a week
        Priority.LOW: 30,       # Within a month
    }

    SYSTEM_PROMPT = """You are a safety risk assessment expert. Your job is to evaluate hazards and assign severity and likelihood scores.

You use a standard 5x5 risk matrix:

SEVERITY SCALE (1-5):
1 = Negligible: Minor first aid, no lost time
2 = Minor: Medical treatment required, minimal lost time
3 = Moderate: Lost time injury, temporary disability
4 = Major: Serious injury, permanent disability possible
5 = Catastrophic: Fatality or multiple serious injuries

LIKELIHOOD SCALE (1-5):
1 = Rare: Unlikely to occur, exceptional circumstances only
2 = Unlikely: Could occur but not expected in normal operations
3 = Possible: May occur during normal operations
4 = Likely: Will probably occur, has happened before in similar situations
5 = Almost Certain: Expected to occur frequently

When assessing hazards:
1. Consider the worst-case realistic outcome for severity
2. Consider exposure frequency and existing controls for likelihood
3. Be consistent and objective in your assessments
4. Provide brief reasoning for your scores

Output valid JSON only."""

    def __init__(self, llm_client: LLMClient | None = None):
        """
        Initialize the Score Manager Agent.

        Args:
            llm_client: Optional LLM client for severity/likelihood assessment
        """
        super().__init__(llm_client)
        self.risk_matrix = RiskMatrixPolicy()
        self.incident_history = IncidentHistoryDB()
        self.metrics_db = MetricsDB()

    def run(self, hazards: list[Hazard]) -> list[ScoredHazard]:
        """
        Score a list of hazards using LLM assessment.

        Args:
            hazards: List of hazards to score

        Returns:
            List of scored hazards with RPN, priority, and due dates

        Raises:
            AgentError: If scoring fails
        """
        try:
            # Get LLM assessments for all hazards at once
            prompt = self._build_prompt(hazards)
            assessments = self.llm_client.extract_json(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT
            )

            logger.info(f"LLM assessed {len(assessments) if assessments else 0} hazards")

            # Create a mapping from hazard_id to assessment
            assessment_map = {}
            if assessments and isinstance(assessments, list):
                for a in assessments:
                    hid = a.get("hazard_id", "")
                    assessment_map[hid] = a

            scored_hazards = []
            for hazard in hazards:
                scored = self._score_hazard(hazard, assessment_map.get(hazard.hazard_id))
                scored_hazards.append(scored)

            logger.info(f"Score Manager produced {len(scored_hazards)} scored hazards")
            return scored_hazards

        except Exception as e:
            logger.error(f"Score Manager failed: {e}", exc_info=True)
            raise AgentError(self.name, f"Failed to score hazards: {e}") from e

    def _score_hazard(self, hazard: Hazard, assessment: dict | None) -> ScoredHazard:
        """
        Score a single hazard using LLM assessment.

        Args:
            hazard: Hazard to score
            assessment: LLM assessment dict or None

        Returns:
            ScoredHazard with all risk metrics
        """
        # Step 1: Get severity and likelihood from LLM assessment
        if assessment:
            severity = self._parse_score(assessment.get("severity"), default=3)
            likelihood = self._parse_score(assessment.get("likelihood"), default=3)
            logger.debug(f"LLM assessment for {hazard.hazard_id}: S={severity}, L={likelihood}")
        else:
            # Fallback to default scores if LLM didn't provide assessment
            logger.warning(f"No LLM assessment for hazard {hazard.hazard_id}, using defaults")
            severity = 3
            likelihood = 3

        # Step 2: Adjust likelihood based on incident history
        adjustment_reason = None
        incident_count = self.incident_history.get_incident_count(
            site=hazard.area or "",
            hazard_type=hazard.taxonomy_ref,
            days_back=30
        )
        if incident_count > 0:
            old_likelihood = likelihood
            likelihood = min(5, likelihood + min(incident_count, 2))
            if likelihood != old_likelihood:
                adjustment_reason = (
                    f"Increased from {old_likelihood} to {likelihood} "
                    f"due to {incident_count} similar incidents in past 30 days"
                )

        # Step 3: Calculate RPN and get priority from risk matrix
        rpn = severity * likelihood
        priority = self.risk_matrix.get_priority(severity, likelihood)

        # Step 4: Calculate due date based on SLA
        sla_days = self.PRIORITY_SLA_DAYS[priority]
        due_by = datetime.now() + timedelta(days=sla_days)

        # Step 5: Calculate culture score delta
        culture_delta = self._calculate_culture_delta(hazard, priority)

        return ScoredHazard(
            hazard_id=hazard.hazard_id,
            severity=severity,
            likelihood=likelihood,
            rpn=rpn,
            priority=priority,
            due_by=due_by,
            culture_score_delta=culture_delta,
            likelihood_adjustment_reason=adjustment_reason,
        )

    def _parse_score(self, value, default: int = 3) -> int:
        """Parse a score value ensuring it's between 1-5."""
        try:
            score = int(value)
            return max(1, min(5, score))
        except (TypeError, ValueError):
            return default

    def _calculate_culture_delta(self, hazard: Hazard, priority: Priority) -> float:
        """
        Calculate the impact on site safety culture score.

        Positive values indicate improvement (e.g., timely reporting).
        Negative values indicate concerns (e.g., recurrent issues).

        Args:
            hazard: The hazard being scored
            priority: Assigned priority level

        Returns:
            Culture score delta (positive or negative float)
        """
        # Base delta: reporting is always positive
        delta = 1.0

        # Penalty for high-severity issues
        if priority == Priority.CRITICAL:
            delta -= 3.0
        elif priority == Priority.HIGH:
            delta -= 1.5

        # Bonus for high-confidence detection (indicates clear reporting)
        if hazard.confidence > 0.8:
            delta += 0.5

        return round(delta, 2)

    def _build_prompt(self, hazards: list[Hazard]) -> str:
        """
        Build the prompt for risk assessment.

        Args:
            hazards: List of hazards to assess

        Returns:
            Formatted prompt for LLM
        """
        hazard_details = []
        for h in hazards:
            hazard_details.append(f"""- Hazard ID: {h.hazard_id}
  Type: {h.type}
  Taxonomy: {h.taxonomy_ref}
  Description: {h.description}
  Area: {h.area or 'Not specified'}""")

        hazards_text = "\n".join(hazard_details)

        return f"""Assess the severity and likelihood for each of the following hazards.

HAZARDS TO ASSESS:
{hazards_text}

For each hazard, provide:
- hazard_id: The exact hazard ID from above
- severity: Score from 1-5 based on potential consequences
- likelihood: Score from 1-5 based on probability of occurrence
- reasoning: Brief explanation of your assessment

Return a JSON array:
[
  {{
    "hazard_id": "exact-hazard-id",
    "severity": 4,
    "likelihood": 3,
    "reasoning": "Brief explanation"
  }}
]

Assess ALL hazards listed above."""
