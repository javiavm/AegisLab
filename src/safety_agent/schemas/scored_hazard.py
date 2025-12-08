"""
ScoredHazard schema - output from the Score Manager Agent.

Extends hazard data with risk scoring (severity, likelihood, RPN, priority)
and culture score impact.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """
    Priority level for hazard remediation.

    Determines SLA and urgency of corrective actions.
    """
    CRITICAL = "CRITICAL"  # Immediate action required
    HIGH = "HIGH"          # Action within 24 hours
    MEDIUM = "MEDIUM"      # Action within 7 days
    LOW = "LOW"            # Action within 30 days


class ScoredHazard(BaseModel):
    """
    A hazard with risk scores computed by the Score Manager Agent.

    Contains the original hazard reference plus computed risk metrics
    based on the risk matrix policy and historical incident data.

    Attributes:
        hazard_id: Reference to the original hazard
        severity: Severity score (1-5, where 5 is most severe)
        likelihood: Likelihood score (1-5, where 5 is most likely)
        rpn: Risk Priority Number (severity × likelihood)
        priority: Derived priority level for action
        due_by: Deadline for corrective action based on SLA
        culture_score_delta: Impact on site's safety culture score
        likelihood_adjustment_reason: Explanation if likelihood was adjusted

    Risk Matrix Reference:
        Severity:
            1 = Negligible (minor first aid)
            2 = Minor (medical treatment)
            3 = Moderate (lost time injury)
            4 = Major (permanent disability)
            5 = Catastrophic (fatality)

        Likelihood:
            1 = Rare (unlikely to occur)
            2 = Unlikely (could occur)
            3 = Possible (may occur)
            4 = Likely (will probably occur)
            5 = Almost Certain (expected to occur)

        RPN Ranges:
            1-4: Low priority
            5-9: Medium priority
            10-15: High priority
            16-25: Critical priority

    Example:
        >>> scored = ScoredHazard(
        ...     hazard_id="haz-456",
        ...     severity=4,
        ...     likelihood=3,
        ...     rpn=12,
        ...     priority=Priority.HIGH,
        ...     due_by=datetime(2025, 11, 25),
        ...     culture_score_delta=-2.5
        ... )
    """

    hazard_id: str = Field(
        ...,
        description="Reference to the original hazard"
    )
    severity: int = Field(
        ...,
        ge=1,
        le=5,
        description="Severity score (1-5)"
    )
    likelihood: int = Field(
        ...,
        ge=1,
        le=5,
        description="Likelihood score (1-5)"
    )
    rpn: int = Field(
        ...,
        ge=1,
        le=25,
        description="Risk Priority Number (severity × likelihood)"
    )
    priority: Priority = Field(
        ...,
        description="Derived priority level"
    )
    due_by: datetime = Field(
        ...,
        description="Deadline for corrective action"
    )
    culture_score_delta: float = Field(
        ...,
        description="Impact on site safety culture score"
    )
    likelihood_adjustment_reason: Optional[str] = Field(
        default=None,
        description="Explanation if likelihood was adjusted based on history"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "hazard_id": "haz-456",
                "severity": 4,
                "likelihood": 3,
                "rpn": 12,
                "priority": "HIGH",
                "due_by": "2025-11-25T17:00:00Z",
                "culture_score_delta": -2.5,
                "likelihood_adjustment_reason": "Increased due to 3 similar incidents in past 30 days"
            }
        }
    }
