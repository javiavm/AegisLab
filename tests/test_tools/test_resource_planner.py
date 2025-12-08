"""
Tests for ResourcePlanner tool.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from safety_agent.tools import ResourcePlanner


class TestResourcePlanner:
    """Tests for ResourcePlanner."""

    @pytest.fixture
    def planner(self):
        """Create planner instance."""
        return ResourcePlanner()

    def test_estimate_labor_cost(self, planner):
        """Test labor cost estimation."""
        cost, lead_time = planner.estimate(
            duration_minutes=60,
            role="safety_engineer",
            materials=[],
        )
        # 1 hour at $75/hour = $75
        assert cost == 75.00

    def test_estimate_with_materials(self, planner):
        """Test estimation including materials."""
        cost, lead_time = planner.estimate(
            duration_minutes=120,
            role="scaffolder",
            materials=["toe_boards", "fixings"],
        )
        # 2 hours at $50/hour = $100
        # toe_boards = $80, fixings = $15
        # Total = $195
        expected_labor = 2 * 50.00
        expected_materials = 80.00 + 15.00
        assert cost == expected_labor + expected_materials

    def test_estimate_lead_time_with_materials(self, planner):
        """Test lead time accounts for material procurement."""
        cost, lead_time = planner.estimate(
            duration_minutes=60,
            role="general_worker",
            materials=["safety_harness"],  # 3 day lead time
        )
        # Should be at least 3 days (material lead time)
        assert lead_time >= 3

    def test_unknown_role_uses_default(self, planner):
        """Test that unknown roles use default rate."""
        cost, _ = planner.estimate(
            duration_minutes=60,
            role="unknown_role",
            materials=[],
        )
        # Should use general_worker rate of $35/hour
        assert cost == 35.00

    def test_get_available_roles(self, planner):
        """Test listing available roles."""
        roles = planner.get_available_roles()
        assert "safety_engineer" in roles
        assert "scaffolder" in roles

    def test_get_available_materials(self, planner):
        """Test listing available materials."""
        materials = planner.get_available_materials()
        assert "safety_barriers" in materials
        assert "toe_boards" in materials
