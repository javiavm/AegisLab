"""
Tests for RiskAnalyzerAgent.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from safety_agent.agents import RiskAnalyzerAgent
from safety_agent.schemas import (
    Observation,
    ObservationPotential,
    ObservationType,
)


class TestRiskAnalyzerAgent:
    """Tests for RiskAnalyzerAgent."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return RiskAnalyzerAgent()

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

    def test_agent_extracts_hazards(self, agent, sample_observation):
        """Test that agent extracts hazards from observation."""
        hazards = agent.run(sample_observation)

        assert len(hazards) > 0
        assert all(h.observation_id == sample_observation.id for h in hazards)

    def test_agent_assigns_taxonomy_refs(self, agent, sample_observation):
        """Test that agent assigns taxonomy references."""
        hazards = agent.run(sample_observation)

        assert all(h.taxonomy_ref.startswith("HAZ-") for h in hazards)

    def test_agent_assigns_confidence_scores(self, agent, sample_observation):
        """Test that agent assigns confidence scores."""
        hazards = agent.run(sample_observation)

        assert all(0.0 <= h.confidence <= 1.0 for h in hazards)

    def test_agent_detects_falling_hazard(self, agent):
        """Test detection of falling-related hazards."""
        obs = Observation(
            observed_at=datetime.now(),
            site="Test Site",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.UNSAFE_CONDITION,
            description="Tool fell from height and nearly hit a worker below.",
        )
        hazards = agent.run(obs)

        # Should detect a falling-related hazard
        taxonomy_refs = [h.taxonomy_ref for h in hazards]
        assert any("FALL" in ref for ref in taxonomy_refs)

    def test_agent_handles_no_clear_hazards(self, agent):
        """Test agent behavior when no clear hazards are identified."""
        obs = Observation(
            observed_at=datetime.now(),
            site="Test Site",
            potential=ObservationPotential.NEAR_MISS,
            type=ObservationType.POSITIVE_OBSERVATION,
            description="Workers observed following all safety procedures correctly.",
        )
        hazards = agent.run(obs)

        # Should still return at least a general safety hazard
        assert len(hazards) > 0
