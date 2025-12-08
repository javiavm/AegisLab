"""
ObservationPipeline - Main orchestration logic for safety observations.

The orchestrator coordinates the three agents without using AI itself.
It's a simple sequential pipeline with validation and error handling.
"""

import json
import logging
from typing import Optional

from pydantic import BaseModel

from safety_agent.schemas import Observation, Hazard, ScoredHazard, ActionPlan
from safety_agent.agents import RiskAnalyzerAgent, ScoreManagerAgent, ActionPlannerAgent
from safety_agent.llm.client import LLMClient

logger = logging.getLogger(__name__)


def _format_json(obj, indent=2) -> str:
    """Format an object as pretty JSON for logging."""
    if hasattr(obj, 'model_dump'):
        return json.dumps(obj.model_dump(), indent=indent, default=str)
    elif isinstance(obj, list):
        return json.dumps([item.model_dump() if hasattr(item, 'model_dump') else item for item in obj], indent=indent, default=str)
    return json.dumps(obj, indent=indent, default=str)


class PipelineResult(BaseModel):
    """
    Result of running the observation pipeline.

    Contains all outputs from each stage of processing.

    Attributes:
        observation: The original input observation
        hazards: Hazards detected by Risk Analyzer
        scored_hazards: Scored hazards from Score Manager
        action_plans: Action plans from Action Planner
        success: Whether the pipeline completed successfully
        error: Error message if pipeline failed
    """
    observation: Observation
    hazards: list[Hazard] = []
    scored_hazards: list[ScoredHazard] = []
    action_plans: list[ActionPlan] = []
    success: bool = True
    error: Optional[str] = None


class ObservationPipeline:
    """
    Orchestrator for the safety observation processing pipeline.

    Coordinates the three agents in sequence:
    1. RiskAnalyzerAgent: Observation → Hazards
    2. ScoreManagerAgent: Hazards → ScoredHazards
    3. ActionPlannerAgent: ScoredHazards → ActionPlans

    The orchestrator is NOT intelligent - it simply routes data
    and handles errors. All reasoning is done by the agents.

    Example:
        >>> pipeline = ObservationPipeline()
        >>> result = pipeline.run(observation)
        >>> print(f"Found {len(result.hazards)} hazards")
        >>> print(f"Generated {len(result.action_plans)} action plans")
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the pipeline with agents.

        Args:
            llm_client: Optional shared LLM client for all agents.
                        If not provided, each agent creates its own.
        """
        self.llm_client = llm_client or LLMClient()

        # Initialize agents with shared LLM client
        self.risk_analyzer = RiskAnalyzerAgent(llm_client=self.llm_client)
        self.score_manager = ScoreManagerAgent(llm_client=self.llm_client)
        self.action_planner = ActionPlannerAgent(llm_client=self.llm_client)

        logger.info("ObservationPipeline initialized with all agents")

    def run(self, observation: Observation) -> PipelineResult:
        """
        Run the full observation processing pipeline.

        Args:
            observation: Safety observation to process

        Returns:
            PipelineResult with outputs from all stages

        Note:
            The pipeline continues even if individual stages partially fail.
            Check the result.success and result.error fields.
        """
        logger.info("=" * 80)
        logger.info("PIPELINE START")
        logger.info("=" * 80)
        logger.info(f"Observation ID: {observation.id}")
        logger.info(f"Site: {observation.site}")
        logger.info(f"Type: {observation.type}")
        logger.info(f"Potential: {observation.potential}")
        logger.info(f"Description: {observation.description}")
        logger.info("-" * 80)

        result = PipelineResult(observation=observation)

        try:
            # ============================================================
            # Stage 1: Risk Analysis
            # ============================================================
            logger.info("")
            logger.info("=" * 80)
            logger.info("STAGE 1: RISK ANALYZER AGENT")
            logger.info("=" * 80)
            logger.info("INPUT (Observation):")
            logger.info(_format_json(observation))
            logger.info("-" * 40)

            result.hazards = self.risk_analyzer.run(observation)

            logger.info(f"OUTPUT: Found {len(result.hazards)} hazard(s)")
            for i, hazard in enumerate(result.hazards):
                logger.info(f"  Hazard #{i+1}:")
                logger.info(f"    - ID: {hazard.hazard_id}")
                logger.info(f"    - Type: {hazard.type}")
                logger.info(f"    - Taxonomy Ref: {hazard.taxonomy_ref}")
                logger.info(f"    - Description: {hazard.description}")
                logger.info(f"    - Area: {hazard.area}")
                logger.info(f"    - Confidence: {hazard.confidence:.2%}")
            logger.info("-" * 80)

            if not result.hazards:
                logger.warning("No hazards detected - pipeline complete")
                return result

            # ============================================================
            # Stage 2: Score Management
            # ============================================================
            logger.info("")
            logger.info("=" * 80)
            logger.info("STAGE 2: SCORE MANAGER AGENT")
            logger.info("=" * 80)
            logger.info(f"INPUT: {len(result.hazards)} hazard(s) from Risk Analyzer")
            logger.info(_format_json(result.hazards))
            logger.info("-" * 40)

            result.scored_hazards = self.score_manager.run(result.hazards)

            logger.info(f"OUTPUT: Scored {len(result.scored_hazards)} hazard(s)")
            for i, scored in enumerate(result.scored_hazards):
                logger.info(f"  Scored Hazard #{i+1}:")
                logger.info(f"    - Hazard ID: {scored.hazard_id}")
                logger.info(f"    - Severity: {scored.severity}/5")
                logger.info(f"    - Likelihood: {scored.likelihood}/5")
                logger.info(f"    - RPN (Risk Priority Number): {scored.rpn}")
                logger.info(f"    - Priority: {scored.priority}")
                logger.info(f"    - Due By: {scored.due_by}")
                logger.info(f"    - Culture Score Delta: {scored.culture_score_delta:+.2f}")
                if scored.likelihood_adjustment_reason:
                    logger.info(f"    - Likelihood Adjustment: {scored.likelihood_adjustment_reason}")
            logger.info("-" * 80)

            # ============================================================
            # Stage 3: Action Planning
            # ============================================================
            logger.info("")
            logger.info("=" * 80)
            logger.info("STAGE 3: ACTION PLANNER AGENT")
            logger.info("=" * 80)
            logger.info(f"INPUT: {len(result.scored_hazards)} scored hazard(s) from Score Manager")
            logger.info(_format_json(result.scored_hazards))
            logger.info("-" * 40)

            # Pass hazard context so ActionPlanner can access original hazard details
            self.action_planner.set_hazard_context(result.hazards)
            result.action_plans = self.action_planner.run(result.scored_hazards)

            logger.info(f"OUTPUT: Generated {len(result.action_plans)} action plan(s)")
            for i, plan in enumerate(result.action_plans):
                logger.info(f"  Action Plan #{i+1}:")
                logger.info(f"    - Plan ID: {plan.plan_id}")
                logger.info(f"    - For Hazard ID: {plan.hazard_id}")
                logger.info(f"    - Standards: {', '.join(plan.standards_refs)}")
                logger.info(f"    - Cost Estimate: ${plan.cost_estimate_usd:.2f}")
                logger.info(f"    - Lead Time: {plan.lead_time_days} day(s)")
                logger.info(f"    - Tasks ({len(plan.tasks)}):")
                for j, task in enumerate(plan.tasks):
                    logger.info(f"        Task #{j+1}: {task.title}")
                    logger.info(f"          - Control Type: {task.control_type}")
                    logger.info(f"          - Responsible: {task.responsible_role}")
                    logger.info(f"          - Duration: {task.duration_minutes} min")
                    logger.info(f"          - Materials: {', '.join(task.material_requirements) or 'None'}")
            logger.info("-" * 80)

            result.success = True

            # ============================================================
            # Pipeline Summary
            # ============================================================
            logger.info("")
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETE - SUMMARY")
            logger.info("=" * 80)
            logger.info(f"  Observation ID: {observation.id}")
            logger.info(f"  Hazards Detected: {len(result.hazards)}")
            logger.info(f"  Hazards Scored: {len(result.scored_hazards)}")
            logger.info(f"  Action Plans Generated: {len(result.action_plans)}")
            total_tasks = sum(len(plan.tasks) for plan in result.action_plans)
            logger.info(f"  Total Tasks Created: {total_tasks}")
            total_cost = sum(plan.cost_estimate_usd for plan in result.action_plans)
            logger.info(f"  Total Estimated Cost: ${total_cost:.2f}")
            logger.info(f"  Status: SUCCESS")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            result.success = False
            result.error = str(e)
            logger.info("")
            logger.info("=" * 80)
            logger.info("PIPELINE FAILED")
            logger.info("=" * 80)
            logger.info(f"  Error: {e}")
            logger.info("=" * 80)

        return result


def run_observation_pipeline(observation: Observation) -> PipelineResult:
    """
    Convenience function to run the observation pipeline.

    Creates a pipeline instance and processes the observation.

    Args:
        observation: Safety observation to process

    Returns:
        PipelineResult with all outputs

    Example:
        >>> from safety_agent.schemas import Observation, ObservationPotential, ObservationType
        >>> from datetime import datetime
        >>>
        >>> observation = Observation(
        ...     observed_at=datetime.now(),
        ...     site="Building A - 3rd floor",
        ...     potential=ObservationPotential.NEAR_MISS,
        ...     type=ObservationType.UNSAFE_CONDITION,
        ...     description="Scaffolding board slipped but worker caught it"
        ... )
        >>> result = run_observation_pipeline(observation)
        >>> print(result.success)
        True
    """
    pipeline = ObservationPipeline()
    return pipeline.run(observation)
