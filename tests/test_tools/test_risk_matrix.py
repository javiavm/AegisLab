"""
Tests for RiskMatrixPolicy tool.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from safety_agent.tools import RiskMatrixPolicy
from safety_agent.schemas import Priority


class TestRiskMatrixPolicy:
    """Tests for RiskMatrixPolicy."""

    @pytest.fixture
    def policy(self):
        """Create policy instance."""
        return RiskMatrixPolicy()

    def test_calculate_rpn(self, policy):
        """Test RPN calculation."""
        assert policy.calculate_rpn(4, 3) == 12
        assert policy.calculate_rpn(1, 1) == 1
        assert policy.calculate_rpn(5, 5) == 25

    def test_rpn_validation(self, policy):
        """Test RPN calculation validates input bounds."""
        with pytest.raises(ValueError):
            policy.calculate_rpn(0, 3)

        with pytest.raises(ValueError):
            policy.calculate_rpn(3, 6)

    def test_critical_priority_for_high_rpn(self, policy):
        """Test that high RPN results in CRITICAL priority."""
        priority = policy.get_priority(severity=4, likelihood=5)
        assert priority == Priority.CRITICAL

    def test_critical_priority_for_severity_5(self, policy):
        """Test that severity 5 always results in CRITICAL."""
        priority = policy.get_priority(severity=5, likelihood=1)
        assert priority == Priority.CRITICAL

    def test_high_priority(self, policy):
        """Test HIGH priority threshold."""
        # RPN of 12 should be HIGH
        priority = policy.get_priority(severity=4, likelihood=3)
        assert priority == Priority.HIGH

    def test_medium_priority(self, policy):
        """Test MEDIUM priority threshold."""
        # RPN of 6 should be MEDIUM
        priority = policy.get_priority(severity=2, likelihood=3)
        assert priority == Priority.MEDIUM

    def test_low_priority(self, policy):
        """Test LOW priority threshold."""
        # RPN of 2 should be LOW
        priority = policy.get_priority(severity=1, likelihood=2)
        assert priority == Priority.LOW

    def test_matrix_display(self, policy):
        """Test matrix display generation."""
        display = policy.get_matrix_display()
        assert "Risk Matrix" in display
        assert "S=5" in display
        assert "L=1" in display
