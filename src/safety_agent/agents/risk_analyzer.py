"""
Risk Analyzer Agent - Detects hazards from safety observations.

Responsibilities:
- Parse observation text to identify potential hazards using LLM
- Normalize hazard types to controlled taxonomy
- Assign confidence scores to detections
"""

import logging

from safety_agent.agents.base import BaseAgent, AgentError
from safety_agent.llm.client import LLMClient
from safety_agent.schemas import Observation, Hazard
from safety_agent.tools.taxonomy_db import TaxonomyDB

logger = logging.getLogger(__name__)


class RiskAnalyzerAgent(BaseAgent[Observation, list[Hazard]]):
    """
    Agent that analyzes observations and extracts hazards using LLM.

    Uses LLM to:
    - Identify hazards mentioned or implied in the observation
    - Extract specific details about each hazard
    - Estimate confidence in the detection

    Uses TaxonomyDB tool to:
    - Normalize detected hazard types to canonical taxonomy refs

    Input: Observation
    Output: list[Hazard]
    """

    name = "RiskAnalyzerAgent"

    SYSTEM_PROMPT = """You are a safety hazard identification expert. Your job is to analyze safety observations and identify all potential hazards.

You have deep knowledge of:
- OSHA regulations and workplace safety standards
- Common industrial hazards (falls, electrical, chemical, mechanical, ergonomic)
- Risk assessment methodologies

When analyzing an observation:
1. Identify ALL hazards, both explicit and implied
2. Be specific about the nature of each hazard
3. Consider contributing factors and root causes
4. Assign confidence based on how clearly the hazard is described

Output valid JSON only."""

    def __init__(self, llm_client: LLMClient | None = None):
        """
        Initialize the Risk Analyzer Agent.

        Args:
            llm_client: Optional LLM client for hazard extraction
        """
        super().__init__(llm_client)
        self.taxonomy_db = TaxonomyDB()

    def run(self, observation: Observation) -> list[Hazard]:
        """
        Analyze an observation and extract hazards using LLM.

        Args:
            observation: Safety observation to analyze

        Returns:
            List of detected hazards with taxonomy refs and confidence

        Raises:
            AgentError: If hazard extraction fails
        """
        try:
            # Step 1: Use LLM to extract raw hazards from text
            prompt = self._build_prompt(observation)
            raw_hazards = self.llm_client.extract_json(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT
            )

            logger.info(f"LLM extracted {len(raw_hazards) if raw_hazards else 0} raw hazards")

            # Handle case where LLM returns empty or invalid response
            if not raw_hazards or not isinstance(raw_hazards, list):
                logger.warning("LLM returned no hazards, using fallback")
                raw_hazards = [{
                    "type": "general_safety",
                    "description": f"Safety concern identified: {observation.description[:100]}",
                    "area": observation.site,
                    "confidence": 0.5
                }]

            # Step 2: Normalize each hazard type via TaxonomyDB
            hazards = []
            for raw in raw_hazards:
                # Validate required fields
                hazard_type = raw.get("type", "general_safety")
                description = raw.get("description", observation.description[:100])
                confidence = raw.get("confidence", 0.5)

                # Ensure confidence is a valid float
                try:
                    confidence = float(confidence)
                    confidence = max(0.0, min(1.0, confidence))
                except (TypeError, ValueError):
                    confidence = 0.5

                taxonomy_ref = self.taxonomy_db.lookup(hazard_type)

                hazard = Hazard(
                    observation_id=observation.id,
                    type=hazard_type,
                    taxonomy_ref=taxonomy_ref,
                    description=description,
                    area=raw.get("area", observation.site),
                    confidence=confidence,
                )
                hazards.append(hazard)

            logger.info(f"Risk Analyzer produced {len(hazards)} hazards")
            return hazards

        except Exception as e:
            logger.error(f"Risk Analyzer failed: {e}", exc_info=True)
            raise AgentError(self.name, f"Failed to analyze observation: {e}") from e

    def _build_prompt(self, observation: Observation) -> str:
        """
        Build the prompt for hazard extraction.

        Args:
            observation: Observation to analyze

        Returns:
            Formatted prompt for LLM
        """
        return f"""Analyze the following safety observation and identify ALL potential hazards.

OBSERVATION DETAILS:
- Site/Location: {observation.site}
- Observation Type: {observation.type.value}
- Potential Severity: {observation.potential.value}
- Description: {observation.description}

For each hazard identified, provide:
- type: A hazard category label (use one of: falling_object, fall_from_height, slip_trip, electrical, electric_shock, chemical_exposure, toxic_fumes, struck_by, caught_in, machinery, ergonomic, manual_handling, fire, explosion, housekeeping, general_safety)
- description: Specific details about this hazard instance
- area: The specific area or zone affected (if identifiable from the observation)
- confidence: Your confidence in this hazard detection (0.0 to 1.0)

Return a JSON array of hazards:
[
  {{
    "type": "hazard_type",
    "description": "specific description of the hazard",
    "area": "affected area",
    "confidence": 0.85
  }}
]

Identify at least one hazard. If multiple hazards are present, list them all."""
