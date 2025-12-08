"""
Tests for Pydantic schema models.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safety_agent.schemas import (
    Observation,
    ObservationPotential,
    ObservationType,
    Hazard,
    ScoredHazard,
    Priority,
    ActionPlan,
    Task,
    ControlHierarchy,
)


class TestObservation:
    """Tests for Observation model."""

    def test_create_observation_with_required_fields(self):
        """Test creating observation with only required fields."""
        obs = Observation(
            observed_at=datetime.now(),
            site="Building A",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.UNSAFE_CONDITION,
            description="Test observation",
        )
        assert obs.id is not None
        assert obs.site == "Building A"
        assert obs.potential == ObservationPotential.NEAR_MISS

    def test_create_observation_from_json(self):
        """Test creating observation from JSON (as would come from API)."""
        json_data = {
            "observedAt": "2025-11-24T10:15:00Z",
            "site": "Building A - 3rd floor",
            "potential": "NEAR_MISS",
            "type": "AREA_FOR_IMPROVEMENT",
            "tradeCategoryId": "trade_cat_1",
            "tradePartnerId": "partner_1",
            "description": "Scaffolding board slipped but worker caught it.",
            "photoId": "file_987"
        }
        obs = Observation.model_validate(json_data)
        assert obs.site == "Building A - 3rd floor"
        assert obs.potential == ObservationPotential.NEAR_MISS
        assert obs.trade_category_id == "trade_cat_1"

    def test_observation_generates_unique_id(self):
        """Test that each observation gets a unique ID."""
        obs1 = Observation(
            observed_at=datetime.now(),
            site="Site 1",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.UNSAFE_ACT,
            description="Test 1",
        )
        obs2 = Observation(
            observed_at=datetime.now(),
            site="Site 2",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.UNSAFE_ACT,
            description="Test 2",
        )
        assert obs1.id != obs2.id


class TestHazard:
    """Tests for Hazard model."""

    def test_create_hazard(self):
        """Test creating a hazard."""
        hazard = Hazard(
            observation_id="obs-123",
            type="falling_object",
            taxonomy_ref="HAZ-FALL-001",
            description="Unsecured scaffolding board",
            confidence=0.85,
        )
        assert hazard.hazard_id is not None
        assert hazard.taxonomy_ref == "HAZ-FALL-001"
        assert hazard.confidence == 0.85

    def test_hazard_confidence_bounds(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            Hazard(
                observation_id="obs-123",
                type="test",
                taxonomy_ref="HAZ-GEN-001",
                description="Test",
                confidence=1.5,  # Invalid
            )


class TestScoredHazard:
    """Tests for ScoredHazard model."""

    def test_create_scored_hazard(self):
        """Test creating a scored hazard."""
        scored = ScoredHazard(
            hazard_id="haz-456",
            severity=4,
            likelihood=3,
            rpn=12,
            priority=Priority.HIGH,
            due_by=datetime.now(),
            culture_score_delta=-2.5,
        )
        assert scored.rpn == 12
        assert scored.priority == Priority.HIGH

    def test_severity_bounds(self):
        """Test that severity must be 1-5."""
        with pytest.raises(ValueError):
            ScoredHazard(
                hazard_id="haz-456",
                severity=6,  # Invalid
                likelihood=3,
                rpn=18,
                priority=Priority.CRITICAL,
                due_by=datetime.now(),
                culture_score_delta=0,
            )


class TestActionPlan:
    """Tests for ActionPlan model."""

    def test_create_action_plan(self):
        """Test creating an action plan with tasks."""
        task = Task(
            title="Install toe boards",
            description="Install 150mm toe boards on all platforms",
            control_type=ControlHierarchy.ENGINEERING,
            responsible_role="scaffolder",
            duration_minutes=120,
            acceptance_criteria="All platforms have toe boards",
        )

        plan = ActionPlan(
            hazard_id="haz-456",
            tasks=[task],
            standards_refs=["OSHA 1926.451"],
            cost_estimate_usd=450.00,
            lead_time_days=2,
        )
        assert len(plan.tasks) == 1
        assert plan.cost_estimate_usd == 450.00

    def test_action_plan_requires_at_least_one_task(self):
        """Test that action plan must have at least one task."""
        with pytest.raises(ValueError):
            ActionPlan(
                hazard_id="haz-456",
                tasks=[],  # Invalid - empty list
                cost_estimate_usd=0,
                lead_time_days=0,
            )
