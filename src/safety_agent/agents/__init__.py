"""
Agents module - AI-powered agents for safety observation processing.

ARCHITECTURE NOTE:
- Agents are "intelligent" components that use LLM for reasoning and extraction.
- Each agent has a specific role in the pipeline and transforms data.
- Agents differ from tools (which are deterministic and rule-based).
- Agents are NOT the orchestrator - they are called BY the orchestrator.

The orchestrator (in orchestrator/pipeline.py) coordinates these agents:
1. RiskAnalyzerAgent receives Observation -> produces Hazards
2. ScoreManagerAgent receives Hazards -> produces ScoredHazards
3. ActionPlannerAgent receives ScoredHazards -> produces ActionPlans

Available agents:
- RiskAnalyzerAgent: Detects hazards from observations
- ScoreManagerAgent: Scores hazards using risk matrices
- ActionPlannerAgent: Generates corrective action plans
"""

from safety_agent.agents.base import BaseAgent
from safety_agent.agents.risk_analyzer import RiskAnalyzerAgent
from safety_agent.agents.score_manager import ScoreManagerAgent
from safety_agent.agents.action_planner import ActionPlannerAgent

__all__ = [
    "BaseAgent",
    "RiskAnalyzerAgent",
    "ScoreManagerAgent",
    "ActionPlannerAgent",
]
