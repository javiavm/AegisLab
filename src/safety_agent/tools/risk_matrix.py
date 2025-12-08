"""
RiskMatrixPolicy - Severity × likelihood grid for RPN and priority.

This is a DETERMINISTIC tool (no AI). It applies a standard risk matrix
to determine priority levels from severity and likelihood scores.
"""

import json
from pathlib import Path
from typing import Optional

from safety_agent.schemas import Priority


class RiskMatrixPolicy:
    """
    Risk matrix policy for calculating RPN and priority.

    Uses a 5×5 risk matrix where:
    - Severity: 1 (negligible) to 5 (catastrophic)
    - Likelihood: 1 (rare) to 5 (almost certain)
    - RPN = Severity × Likelihood (1-25)

    Priority thresholds:
    - CRITICAL: RPN >= 16 or Severity = 5
    - HIGH: RPN >= 10
    - MEDIUM: RPN >= 5
    - LOW: RPN < 5

    Example:
        >>> policy = RiskMatrixPolicy()
        >>> priority = policy.get_priority(severity=4, likelihood=3)
        >>> print(priority)
        Priority.HIGH
    """

    # Default priority thresholds
    DEFAULT_THRESHOLDS = {
        "critical_rpn": 16,
        "high_rpn": 10,
        "medium_rpn": 5,
        "critical_severity": 5,  # Any severity=5 is critical regardless of RPN
    }

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the RiskMatrixPolicy.

        Args:
            config_file: Optional path to risk matrix JSON config.
                         If not provided, uses default thresholds.
        """
        if config_file and config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                self._thresholds = config.get("thresholds", self.DEFAULT_THRESHOLDS)
        else:
            self._thresholds = self.DEFAULT_THRESHOLDS.copy()

    def calculate_rpn(self, severity: int, likelihood: int) -> int:
        """
        Calculate Risk Priority Number.

        Args:
            severity: Severity score (1-5)
            likelihood: Likelihood score (1-5)

        Returns:
            RPN value (1-25)

        Raises:
            ValueError: If scores are out of range
        """
        if not (1 <= severity <= 5):
            raise ValueError(f"Severity must be 1-5, got {severity}")
        if not (1 <= likelihood <= 5):
            raise ValueError(f"Likelihood must be 1-5, got {likelihood}")

        return severity * likelihood

    def get_priority(self, severity: int, likelihood: int) -> Priority:
        """
        Determine priority level from severity and likelihood.

        Args:
            severity: Severity score (1-5)
            likelihood: Likelihood score (1-5)

        Returns:
            Priority level (CRITICAL, HIGH, MEDIUM, or LOW)
        """
        rpn = self.calculate_rpn(severity, likelihood)

        # Check for critical severity override
        if severity >= self._thresholds["critical_severity"]:
            return Priority.CRITICAL

        # Check RPN thresholds
        if rpn >= self._thresholds["critical_rpn"]:
            return Priority.CRITICAL
        elif rpn >= self._thresholds["high_rpn"]:
            return Priority.HIGH
        elif rpn >= self._thresholds["medium_rpn"]:
            return Priority.MEDIUM
        else:
            return Priority.LOW

    def get_matrix(self) -> dict[tuple[int, int], Priority]:
        """
        Get the full risk matrix as a dictionary.

        Returns:
            Dict mapping (severity, likelihood) tuples to Priority
        """
        matrix = {}
        for severity in range(1, 6):
            for likelihood in range(1, 6):
                matrix[(severity, likelihood)] = self.get_priority(severity, likelihood)
        return matrix

    def get_matrix_display(self) -> str:
        """
        Get a text representation of the risk matrix for display.

        Returns:
            Formatted string showing the 5×5 matrix
        """
        lines = ["Risk Matrix (Severity × Likelihood → Priority)", ""]
        lines.append("         | L=1    L=2    L=3    L=4    L=5")
        lines.append("-" * 50)

        for severity in range(5, 0, -1):
            row = f"S={severity}     |"
            for likelihood in range(1, 6):
                priority = self.get_priority(severity, likelihood)
                # Abbreviate priority names
                abbrev = {
                    Priority.CRITICAL: "CRIT",
                    Priority.HIGH: "HIGH",
                    Priority.MEDIUM: "MED ",
                    Priority.LOW: "LOW ",
                }[priority]
                row += f" {abbrev}  "
            lines.append(row)

        return "\n".join(lines)
