"""
Pydantic schemas for the safety observation workflow.

These models define the data structures flowing through the pipeline:
- Observation: Input from users (the canonical input)
- Hazard: Detected hazards from Risk Analyzer
- ScoredHazard: Hazards with risk scores from Score Manager
- ActionPlan: Corrective actions from Action Planner
"""

from safety_agent.schemas.observation import Observation, ObservationPotential, ObservationType
from safety_agent.schemas.hazard import Hazard
from safety_agent.schemas.scored_hazard import ScoredHazard, Priority
from safety_agent.schemas.action_plan import ActionPlan, Task, ControlHierarchy

__all__ = [
    "Observation",
    "ObservationPotential",
    "ObservationType",
    "Hazard",
    "ScoredHazard",
    "Priority",
    "ActionPlan",
    "Task",
    "ControlHierarchy",
]
