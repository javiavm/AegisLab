"""
MetricsDB - Safety culture scores per site.

This is a DETERMINISTIC tool (no AI). It tracks and updates
safety culture scores for each site based on observations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class MetricsDB:
    """
    Database for safety culture metrics.

    Tracks a "culture score" per site, which represents the overall
    safety culture health. The score is affected by:
    - Positive: Timely reporting, proactive observations
    - Negative: Recurring hazards, high-severity incidents

    For the PoC, this is an in-memory store.
    In production, this would persist to a real database.

    Example:
        >>> db = MetricsDB()
        >>> score = db.get_culture_score("Building A")
        >>> print(score)
        75.0
        >>> db.update_culture_score("Building A", delta=-2.5)
        >>> print(db.get_culture_score("Building A"))
        72.5
    """

    # Default starting score for new sites
    DEFAULT_SCORE = 75.0

    # Score bounds
    MIN_SCORE = 0.0
    MAX_SCORE = 100.0

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize the MetricsDB.

        Args:
            data_file: Optional path to metrics JSON file.
                       If not provided, uses empty in-memory store.
        """
        self._scores: dict[str, float] = {}
        self._history: list[dict] = []

        if data_file and data_file.exists():
            with open(data_file) as f:
                data = json.load(f)
                self._scores = data.get("scores", {})
                self._history = data.get("history", [])

    def get_culture_score(self, site: str) -> float:
        """
        Get the current culture score for a site.

        Args:
            site: Site identifier

        Returns:
            Current culture score (0-100)
        """
        # Normalize site name for consistent lookup
        normalized_site = self._normalize_site(site)
        return self._scores.get(normalized_site, self.DEFAULT_SCORE)

    def update_culture_score(
        self,
        site: str,
        delta: float,
        reason: Optional[str] = None
    ) -> float:
        """
        Update the culture score for a site.

        Args:
            site: Site identifier
            delta: Amount to add/subtract from current score
            reason: Optional reason for the update

        Returns:
            New culture score after update
        """
        normalized_site = self._normalize_site(site)
        current = self._scores.get(normalized_site, self.DEFAULT_SCORE)
        new_score = max(self.MIN_SCORE, min(self.MAX_SCORE, current + delta))

        self._scores[normalized_site] = new_score

        # Record history
        self._history.append({
            "site": normalized_site,
            "old_score": current,
            "new_score": new_score,
            "delta": delta,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })

        return new_score

    def get_all_scores(self) -> dict[str, float]:
        """
        Get culture scores for all tracked sites.

        Returns:
            Dict mapping site names to scores
        """
        return self._scores.copy()

    def get_history(
        self,
        site: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Get score update history.

        Args:
            site: Optional site filter
            limit: Maximum number of records to return

        Returns:
            List of history records (most recent first)
        """
        history = self._history.copy()

        if site:
            normalized_site = self._normalize_site(site)
            history = [h for h in history if h["site"] == normalized_site]

        # Sort by timestamp descending and limit
        history.sort(key=lambda h: h["timestamp"], reverse=True)
        return history[:limit]

    def _normalize_site(self, site: str) -> str:
        """
        Normalize site name for consistent storage.

        Args:
            site: Raw site name

        Returns:
            Normalized site name
        """
        # Simple normalization: lowercase, strip whitespace
        return site.lower().strip()

    def save(self, data_file: Path) -> None:
        """
        Save metrics to a JSON file.

        Args:
            data_file: Path to save the data
        """
        data = {
            "scores": self._scores,
            "history": self._history,
        }
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
