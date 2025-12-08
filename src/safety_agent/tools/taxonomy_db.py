"""
TaxonomyDB - Maps hazard labels to canonical taxonomy references.

This is a DETERMINISTIC tool (no AI). It performs simple lookups
against a controlled vocabulary of hazard types.
"""

import json
from pathlib import Path
from typing import Optional


class TaxonomyDB:
    """
    Taxonomy database for hazard type normalization.

    Maps free-form hazard labels (e.g., "falling_object", "slip", "fall")
    to canonical taxonomy references (e.g., "HAZ-FALL-001").

    This enables consistent hazard classification across the system.

    Example:
        >>> db = TaxonomyDB()
        >>> ref = db.lookup("falling_object")
        >>> print(ref)
        "HAZ-FALL-001"
    """

    # Default taxonomy mapping (used if no JSON file is loaded)
    DEFAULT_TAXONOMY = {
        # Falling hazards
        "falling_object": "HAZ-FALL-001",
        "fall_from_height": "HAZ-FALL-001",
        "fall": "HAZ-FALL-001",
        "dropped_object": "HAZ-FALL-001",
        "slip": "HAZ-FALL-002",
        "trip": "HAZ-FALL-002",
        "slip_trip": "HAZ-FALL-002",

        # Electrical hazards
        "electrical": "HAZ-ELEC-001",
        "electric_shock": "HAZ-ELEC-001",
        "exposed_wiring": "HAZ-ELEC-001",
        "arc_flash": "HAZ-ELEC-002",

        # Chemical hazards
        "chemical_exposure": "HAZ-CHEM-001",
        "chemical": "HAZ-CHEM-001",
        "spill": "HAZ-CHEM-001",
        "toxic_fumes": "HAZ-CHEM-002",
        "fumes": "HAZ-CHEM-002",

        # Mechanical hazards
        "struck_by": "HAZ-MECH-001",
        "caught_in": "HAZ-MECH-002",
        "machinery": "HAZ-MECH-001",
        "moving_equipment": "HAZ-MECH-001",

        # Ergonomic hazards
        "ergonomic": "HAZ-ERGO-001",
        "manual_handling": "HAZ-ERGO-001",
        "repetitive_motion": "HAZ-ERGO-002",

        # Fire hazards
        "fire": "HAZ-FIRE-001",
        "explosion": "HAZ-FIRE-002",
        "hot_work": "HAZ-FIRE-001",

        # General/other
        "general_safety": "HAZ-GEN-001",
        "housekeeping": "HAZ-GEN-002",
        "unknown": "HAZ-GEN-001",
    }

    # Unknown hazard fallback
    UNKNOWN_REF = "HAZ-GEN-001"

    def __init__(self, taxonomy_file: Optional[Path] = None):
        """
        Initialize the TaxonomyDB.

        Args:
            taxonomy_file: Optional path to taxonomy JSON file.
                           If not provided, uses default taxonomy.
        """
        if taxonomy_file and taxonomy_file.exists():
            with open(taxonomy_file) as f:
                self._taxonomy = json.load(f)
        else:
            self._taxonomy = self.DEFAULT_TAXONOMY.copy()

    def lookup(self, hazard_type: str) -> str:
        """
        Look up the canonical taxonomy reference for a hazard type.

        Args:
            hazard_type: Raw hazard type label (case-insensitive)

        Returns:
            Canonical taxonomy reference (e.g., "HAZ-FALL-001")
        """
        normalized = hazard_type.lower().strip().replace(" ", "_")
        return self._taxonomy.get(normalized, self.UNKNOWN_REF)

    def get_all_types(self) -> list[str]:
        """
        Get all known hazard types.

        Returns:
            List of hazard type labels
        """
        return list(self._taxonomy.keys())

    def get_all_refs(self) -> set[str]:
        """
        Get all unique taxonomy references.

        Returns:
            Set of canonical taxonomy references
        """
        return set(self._taxonomy.values())

    def reverse_lookup(self, taxonomy_ref: str) -> list[str]:
        """
        Find all hazard types that map to a given taxonomy reference.

        Args:
            taxonomy_ref: Canonical taxonomy reference

        Returns:
            List of hazard type labels that map to this reference
        """
        return [
            hazard_type
            for hazard_type, ref in self._taxonomy.items()
            if ref == taxonomy_ref
        ]
