"""
Orchestrator module - Pipeline coordinator for safety observation workflow.

ARCHITECTURE NOTE:
The orchestrator is a RUNTIME COORDINATOR, not an intelligent agent.
It does NOT use LLM - it simply:
1. Routes data between agents in sequence
2. Validates schemas at each step
3. Handles errors and logging
4. Returns the final aggregated result

Flow:
    Observation
        │
        ▼
    RiskAnalyzerAgent → list[Hazard]
        │
        ▼
    ScoreManagerAgent → list[ScoredHazard]
        │
        ▼
    ActionPlannerAgent → list[ActionPlan]
        │
        ▼
    PipelineResult
"""

from safety_agent.orchestrator.pipeline import (
    ObservationPipeline,
    PipelineResult,
    run_observation_pipeline,
)

__all__ = [
    "ObservationPipeline",
    "PipelineResult",
    "run_observation_pipeline",
]
