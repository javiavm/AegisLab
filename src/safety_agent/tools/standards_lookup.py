"""
StandardsLookup - OSHA/ISO 45001 clause lookup by hazard type.

This is a DETERMINISTIC tool (no AI). It returns applicable safety
standard references for different hazard types.
"""

import json
from pathlib import Path
from typing import Optional


class StandardsLookup:
    """
    Lookup service for safety standard references.

    Maps hazard taxonomy references to applicable standards from:
    - OSHA regulations (29 CFR 1926 for construction)
    - ISO 45001:2018 (Occupational Health & Safety)

    For the PoC, this uses a static mapping. In production,
    this could query a more comprehensive standards database.

    Example:
        >>> lookup = StandardsLookup()
        >>> refs = lookup.get_standards_for_hazard("HAZ-FALL-001")
        >>> print(refs)
        ["OSHA 1926.451", "OSHA 1926.502", "ISO 45001:2018 8.1.2"]
    """

    # Default standards mapping
    DEFAULT_STANDARDS = {
        # Falling hazards
        "HAZ-FALL-001": {
            "osha": [
                "OSHA 1926.451 - Scaffolding",
                "OSHA 1926.502 - Fall protection systems",
                "OSHA 1926.503 - Fall protection training",
            ],
            "iso": [
                "ISO 45001:2018 6.1.2 - Hazard identification",
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
            ],
            "description": "Standards for fall prevention and protection",
        },
        "HAZ-FALL-002": {
            "osha": [
                "OSHA 1926.25 - Housekeeping",
                "OSHA 1910.22 - Walking-working surfaces",
            ],
            "iso": [
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
            ],
            "description": "Standards for slip, trip and fall prevention",
        },

        # Electrical hazards
        "HAZ-ELEC-001": {
            "osha": [
                "OSHA 1926.405 - Wiring methods",
                "OSHA 1926.416 - General electrical safety",
                "OSHA 1926.417 - Lockout/tagout",
            ],
            "iso": [
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
                "ISO 45001:2018 8.2 - Emergency preparedness",
            ],
            "description": "Standards for electrical safety",
        },
        "HAZ-ELEC-002": {
            "osha": [
                "OSHA 1910.269 - Electric power generation",
                "NFPA 70E - Electrical Safety in the Workplace",
            ],
            "iso": [
                "ISO 45001:2018 8.2 - Emergency preparedness",
            ],
            "description": "Standards for arc flash protection",
        },

        # Chemical hazards
        "HAZ-CHEM-001": {
            "osha": [
                "OSHA 1926.55 - Gases, vapors, fumes",
                "OSHA 1910.1200 - Hazard Communication",
                "OSHA 1926.59 - Hazard Communication (construction)",
            ],
            "iso": [
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
                "ISO 45001:2018 7.4 - Communication",
            ],
            "description": "Standards for chemical exposure control",
        },
        "HAZ-CHEM-002": {
            "osha": [
                "OSHA 1910.134 - Respiratory Protection",
                "OSHA 1926.103 - Respiratory protection (construction)",
            ],
            "iso": [
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
            ],
            "description": "Standards for toxic fumes protection",
        },

        # Mechanical hazards
        "HAZ-MECH-001": {
            "osha": [
                "OSHA 1926.600 - Equipment (general)",
                "OSHA 1926.602 - Material handling equipment",
            ],
            "iso": [
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
            ],
            "description": "Standards for struck-by hazards",
        },
        "HAZ-MECH-002": {
            "osha": [
                "OSHA 1910.212 - Machine guarding",
                "OSHA 1910.147 - Control of hazardous energy",
            ],
            "iso": [
                "ISO 45001:2018 8.1.2 - Eliminating hazards",
            ],
            "description": "Standards for caught-in hazards",
        },

        # Ergonomic hazards
        "HAZ-ERGO-001": {
            "osha": [
                "OSHA General Duty Clause 5(a)(1)",
                "NIOSH Lifting Equation",
            ],
            "iso": [
                "ISO 45001:2018 6.1.2 - Hazard identification",
                "ISO 11228 - Ergonomics - Manual handling",
            ],
            "description": "Standards for manual handling",
        },

        # Fire hazards
        "HAZ-FIRE-001": {
            "osha": [
                "OSHA 1926.352 - Fire prevention",
                "OSHA 1910.39 - Fire prevention plans",
            ],
            "iso": [
                "ISO 45001:2018 8.2 - Emergency preparedness",
            ],
            "description": "Standards for fire prevention",
        },

        # General
        "HAZ-GEN-001": {
            "osha": [
                "OSHA General Duty Clause 5(a)(1)",
                "OSHA 1926.20 - General safety and health provisions",
            ],
            "iso": [
                "ISO 45001:2018 6.1 - Actions to address risks",
                "ISO 45001:2018 8.1 - Operational planning and control",
            ],
            "description": "General safety standards",
        },
        "HAZ-GEN-002": {
            "osha": [
                "OSHA 1926.25 - Housekeeping",
            ],
            "iso": [
                "ISO 45001:2018 8.1 - Operational planning and control",
            ],
            "description": "Standards for housekeeping",
        },
    }

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize the StandardsLookup.

        Args:
            data_file: Optional path to standards JSON file.
                       If not provided, uses default standards.
        """
        if data_file and data_file.exists():
            with open(data_file) as f:
                self._standards = json.load(f)
        else:
            self._standards = self.DEFAULT_STANDARDS.copy()

    def get_standards_for_hazard(self, taxonomy_ref: str) -> list[str]:
        """
        Get applicable standard references for a hazard type.

        Args:
            taxonomy_ref: Hazard taxonomy reference (e.g., "HAZ-FALL-001")

        Returns:
            List of standard references (OSHA + ISO combined)
        """
        standards_data = self._standards.get(
            taxonomy_ref,
            self._standards.get("HAZ-GEN-001", {})
        )

        refs = []
        refs.extend(standards_data.get("osha", []))
        refs.extend(standards_data.get("iso", []))
        return refs

    def get_osha_standards(self, taxonomy_ref: str) -> list[str]:
        """
        Get OSHA-specific standards for a hazard type.

        Args:
            taxonomy_ref: Hazard taxonomy reference

        Returns:
            List of OSHA standard references
        """
        standards_data = self._standards.get(taxonomy_ref, {})
        return standards_data.get("osha", [])

    def get_iso_standards(self, taxonomy_ref: str) -> list[str]:
        """
        Get ISO 45001 standards for a hazard type.

        Args:
            taxonomy_ref: Hazard taxonomy reference

        Returns:
            List of ISO standard references
        """
        standards_data = self._standards.get(taxonomy_ref, {})
        return standards_data.get("iso", [])

    def get_description(self, taxonomy_ref: str) -> str:
        """
        Get a description of standards applicable to a hazard type.

        Args:
            taxonomy_ref: Hazard taxonomy reference

        Returns:
            Description string
        """
        standards_data = self._standards.get(taxonomy_ref, {})
        return standards_data.get("description", "General safety standards")
