"""
Tools module - Deterministic services used by agents.

ARCHITECTURE NOTE:
- Tools are DETERMINISTIC - no AI/LLM inside them.
- Tools are pure functions or stateful services with predictable behavior.
- Tools are called BY agents to perform specific operations.
- Tools differ from agents (which use LLM for reasoning).

Available tools:
- TaxonomyDB: Maps hazard labels to canonical taxonomy references
- RiskMatrixPolicy: Severity × likelihood grid for RPN and priority
- IncidentHistoryDB: Historical incident data for likelihood adjustment
- MetricsDB: Safety culture scores per site
- StandardsLookup: OSHA/ISO 45001 clause lookup by hazard type
- ResourcePlanner: Cost and lead time calculator for tasks
"""

from safety_agent.tools.taxonomy_db import TaxonomyDB
from safety_agent.tools.risk_matrix import RiskMatrixPolicy
from safety_agent.tools.incident_history import IncidentHistoryDB
from safety_agent.tools.metrics_db import MetricsDB
from safety_agent.tools.standards_lookup import StandardsLookup
from safety_agent.tools.resource_planner import ResourcePlanner

__all__ = [
    "TaxonomyDB",
    "RiskMatrixPolicy",
    "IncidentHistoryDB",
    "MetricsDB",
    "StandardsLookup",
    "ResourcePlanner",
]
