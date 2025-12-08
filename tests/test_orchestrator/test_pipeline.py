"""
Tests for ObservationPipeline orchestrator.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from safety_agent.orchestrator import ObservationPipeline, run_observation_pipeline
from safety_agent.schemas import (
    Observation,
    ObservationPotential,
    ObservationType,
)


class TestObservationPipeline:
    """Tests for ObservationPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return ObservationPipeline()

    @pytest.fixture
    def sample_observation(self):
        """Create sample observation for testing."""
        return Observation(
            observed_at=datetime.now(),
            site="Building A - 3rd floor",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.UNSAFE_CONDITION,
            description="Scaffolding board slipped but worker caught it before falling.",
        )

    def test_pipeline_returns_result(self, pipeline, sample_observation):
        """Test that pipeline returns a PipelineResult."""
        result = pipeline.run(sample_observation)

        assert result is not None
        assert result.observation.id == sample_observation.id

    def test_pipeline_extracts_hazards(self, pipeline, sample_observation):
        """Test that pipeline extracts hazards."""
        result = pipeline.run(sample_observation)

        assert len(result.hazards) > 0
        assert all(h.observation_id == sample_observation.id for h in result.hazards)

    def test_pipeline_scores_hazards(self, pipeline, sample_observation):
        """Test that pipeline scores hazards."""
        result = pipeline.run(sample_observation)

        assert len(result.scored_hazards) == len(result.hazards)
        assert all(sh.severity >= 1 for sh in result.scored_hazards)
        assert all(sh.severity <= 5 for sh in result.scored_hazards)

    def test_pipeline_generates_action_plans(self, pipeline, sample_observation):
        """Test that pipeline generates action plans."""
        result = pipeline.run(sample_observation)

        assert len(result.action_plans) > 0
        assert all(len(ap.tasks) > 0 for ap in result.action_plans)

    def test_pipeline_success_flag(self, pipeline, sample_observation):
        """Test that successful pipeline sets success flag."""
        result = pipeline.run(sample_observation)

        assert result.success is True
        assert result.error is None

    def test_convenience_function(self, sample_observation):
        """Test run_observation_pipeline convenience function."""
        result = run_observation_pipeline(sample_observation)

        assert result is not None
        assert result.success is True
        assert len(result.hazards) > 0


class TestPipelineIntegration:
    """Integration tests for the full pipeline."""

    def test_full_pipeline_with_scaffolding_observation(self):
        """Test full pipeline with realistic scaffolding observation."""
        observation = Observation(
            observed_at=datetime.now(),
            site="Building A - 3rd floor",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.UNSAFE_CONDITION,
            description=(
                "Scaffolding board slipped but worker caught it before falling. "
                "The board was not properly secured with toe boards. "
                "Worker was wearing harness but it was not attached."
            ),
            trade_category_id="scaffolding",
            trade_partner_id="partner_001",
        )

        result = run_observation_pipeline(observation)

        # Verify full pipeline execution
        assert result.success
        assert len(result.hazards) > 0
        assert len(result.scored_hazards) == len(result.hazards)
        assert len(result.action_plans) == len(result.scored_hazards)

        # Verify action plans have standards references
        for plan in result.action_plans:
            assert len(plan.standards_refs) > 0
            assert plan.cost_estimate_usd > 0
            assert plan.lead_time_days >= 0

    def test_full_pipeline_with_electrical_observation(self):
        """Test full pipeline with electrical hazard observation."""
        observation = Observation(
            observed_at=datetime.now(),
            site="Building B - Electrical room",
            potential=ObservationPotential.MEDICAL_TREATMENT,
            type=ObservationType.UNSAFE_CONDITION,
            description="Exposed electrical wiring found near water source.",
        )

        result = run_observation_pipeline(observation)

        assert result.success
        assert len(result.hazards) > 0

        # Check that electrical hazard was detected
        taxonomy_refs = [h.taxonomy_ref for h in result.hazards]
        assert any("ELEC" in ref for ref in taxonomy_refs)
