"""
Hazard schema - output from the Risk Analyzer Agent.

Represents a detected hazard extracted from an observation,
normalized to a controlled taxonomy.
"""

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Hazard(BaseModel):
    """
    A detected hazard extracted from an observation.

    Produced by the Risk Analyzer Agent after parsing the observation
    text and normalizing hazard types to the controlled taxonomy.

    Attributes:
        hazard_id: Unique identifier for this hazard
        observation_id: Reference to the source observation
        type: Raw hazard type as detected (before normalization)
        taxonomy_ref: Normalized reference to controlled taxonomy
        description: Extracted description of the specific hazard
        area: Specific area/zone within the site (if identifiable)
        confidence: Agent's confidence in the hazard detection (0.0-1.0)

    Example:
        >>> hazard = Hazard(
        ...     observation_id="obs-123",
        ...     type="falling_object",
        ...     taxonomy_ref="HAZ-FALL-001",
        ...     description="Unsecured scaffolding board at height",
        ...     area="3rd floor scaffolding",
        ...     confidence=0.85
        ... )
    """

    hazard_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this hazard"
    )
    observation_id: str = Field(
        ...,
        description="Reference to the source observation"
    )
    type: str = Field(
        ...,
        description="Raw hazard type as detected"
    )
    taxonomy_ref: str = Field(
        ...,
        description="Normalized taxonomy reference (e.g., HAZ-FALL-001)"
    )
    description: str = Field(
        ...,
        description="Specific description of the hazard"
    )
    area: Optional[str] = Field(
        default=None,
        description="Specific area within the site"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence score (0.0-1.0)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "hazard_id": "haz-456",
                "observation_id": "obs-123",
                "type": "falling_object",
                "taxonomy_ref": "HAZ-FALL-001",
                "description": "Unsecured scaffolding board at height",
                "area": "3rd floor scaffolding",
                "confidence": 0.85
            }
        }
    }
