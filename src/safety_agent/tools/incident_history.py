"""
IncidentHistoryDB - Historical incident data for likelihood adjustment.

This is a DETERMINISTIC tool (no AI). It provides historical incident
counts to adjust risk likelihood scores based on past occurrences.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class IncidentHistoryDB:
    """
    Database of historical safety incidents.

    Used by ScoreManagerAgent to adjust likelihood scores based on
    how often similar incidents have occurred in the past.

    For the PoC, this is an in-memory store with fake data.
    In production, this would query an actual incident database.

    Example:
        >>> db = IncidentHistoryDB()
        >>> count = db.get_incident_count(
        ...     site="Building A",
        ...     hazard_type="HAZ-FALL-001",
        ...     days_back=30
        ... )
        >>> print(count)
        3
    """

    # Sample incident data for PoC testing
    DEFAULT_INCIDENTS = [
        {
            "incident_id": "INC-001",
            "site": "Building A - 3rd floor",
            "hazard_type": "HAZ-FALL-001",
            "date": "2025-11-15",
            "severity": "near_miss",
        },
        {
            "incident_id": "INC-002",
            "site": "Building A - 3rd floor",
            "hazard_type": "HAZ-FALL-001",
            "date": "2025-11-10",
            "severity": "first_aid",
        },
        {
            "incident_id": "INC-003",
            "site": "Building A - 2nd floor",
            "hazard_type": "HAZ-ELEC-001",
            "date": "2025-11-20",
            "severity": "near_miss",
        },
        {
            "incident_id": "INC-004",
            "site": "Building B",
            "hazard_type": "HAZ-CHEM-001",
            "date": "2025-10-25",
            "severity": "first_aid",
        },
        {
            "incident_id": "INC-005",
            "site": "Building A - 3rd floor",
            "hazard_type": "HAZ-FALL-001",
            "date": "2025-11-22",
            "severity": "near_miss",
        },
    ]

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize the IncidentHistoryDB.

        Args:
            data_file: Optional path to incidents JSON file.
                       If not provided, uses default sample data.
        """
        if data_file and data_file.exists():
            with open(data_file) as f:
                self._incidents = json.load(f)
        else:
            self._incidents = self.DEFAULT_INCIDENTS.copy()

        # Parse dates
        for incident in self._incidents:
            if isinstance(incident["date"], str):
                incident["date"] = datetime.fromisoformat(incident["date"])

    def get_incident_count(
        self,
        site: str,
        hazard_type: str,
        days_back: int = 30
    ) -> int:
        """
        Count incidents matching the criteria within the time window.

        Args:
            site: Site location (partial match supported)
            hazard_type: Taxonomy reference (exact match)
            days_back: Number of days to look back

        Returns:
            Number of matching incidents
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        count = 0

        for incident in self._incidents:
            # Check date
            incident_date = incident["date"]
            if isinstance(incident_date, str):
                incident_date = datetime.fromisoformat(incident_date)

            if incident_date < cutoff_date:
                continue

            # Check hazard type (exact match)
            if incident["hazard_type"] != hazard_type:
                continue

            # Check site (partial match - site contains the search term or vice versa)
            incident_site = incident["site"].lower()
            search_site = site.lower()
            if search_site not in incident_site and incident_site not in search_site:
                continue

            count += 1

        return count

    def get_incidents_by_site(self, site: str) -> list[dict]:
        """
        Get all incidents for a site.

        Args:
            site: Site location (partial match supported)

        Returns:
            List of incident records
        """
        results = []
        search_site = site.lower()

        for incident in self._incidents:
            incident_site = incident["site"].lower()
            if search_site in incident_site or incident_site in search_site:
                results.append(incident)

        return results

    def add_incident(
        self,
        site: str,
        hazard_type: str,
        severity: str,
        date: Optional[datetime] = None
    ) -> dict:
        """
        Add a new incident record.

        Args:
            site: Site location
            hazard_type: Taxonomy reference
            severity: Severity classification
            date: Incident date (defaults to now)

        Returns:
            The created incident record
        """
        incident = {
            "incident_id": f"INC-{len(self._incidents) + 1:03d}",
            "site": site,
            "hazard_type": hazard_type,
            "date": date or datetime.now(),
            "severity": severity,
        }
        self._incidents.append(incident)
        return incident
