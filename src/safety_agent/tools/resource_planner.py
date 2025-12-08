"""
ResourcePlanner - Cost and lead time calculator for corrective tasks.

This is a DETERMINISTIC tool (no AI). It calculates estimated costs
and lead times based on task parameters and hardcoded rate tables.
"""

import json
from pathlib import Path
from typing import Optional


class ResourcePlanner:
    """
    Resource planning calculator for corrective action tasks.

    Estimates:
    - Labor cost based on duration and role hourly rates
    - Material cost based on required materials
    - Lead time based on material availability and task complexity

    For the PoC, uses hardcoded rate tables. In production,
    this could integrate with procurement/HR systems.

    Example:
        >>> planner = ResourcePlanner()
        >>> cost, lead_time = planner.estimate(
        ...     duration_minutes=120,
        ...     role="safety_engineer",
        ...     materials=["safety_barriers", "warning_signs"]
        ... )
        >>> print(f"Cost: ${cost}, Lead time: {lead_time} days")
        Cost: $230.0, Lead time: 2 days
    """

    # Default labor rates (USD per hour)
    DEFAULT_LABOR_RATES = {
        "safety_engineer": 75.00,
        "safety_officer": 55.00,
        "supervisor": 45.00,
        "scaffolder": 50.00,
        "electrician": 65.00,
        "general_worker": 35.00,
        "contractor": 85.00,
    }

    # Default material costs (USD)
    DEFAULT_MATERIAL_COSTS = {
        "safety_barriers": 150.00,
        "warning_signs": 25.00,
        "toe_boards": 80.00,
        "fixings": 15.00,
        "training_materials": 50.00,
        "ppe_checklist": 5.00,
        "hard_hat": 30.00,
        "safety_glasses": 15.00,
        "safety_harness": 200.00,
        "fire_extinguisher": 75.00,
        "first_aid_kit": 45.00,
        "lockout_tagout_kit": 120.00,
        "respirator": 85.00,
        "chemical_gloves": 20.00,
        "spill_kit": 150.00,
    }

    # Default lead times for materials (days)
    DEFAULT_MATERIAL_LEAD_TIMES = {
        "safety_barriers": 2,
        "warning_signs": 1,
        "toe_boards": 2,
        "fixings": 1,
        "training_materials": 1,
        "ppe_checklist": 0,
        "hard_hat": 1,
        "safety_glasses": 1,
        "safety_harness": 3,
        "fire_extinguisher": 2,
        "first_aid_kit": 1,
        "lockout_tagout_kit": 3,
        "respirator": 2,
        "chemical_gloves": 1,
        "spill_kit": 2,
    }

    # Base lead time for any task (days)
    BASE_LEAD_TIME = 1

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the ResourcePlanner.

        Args:
            config_file: Optional path to rates JSON file.
                         If not provided, uses default rates.
        """
        if config_file and config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                self._labor_rates = config.get("labor_rates", self.DEFAULT_LABOR_RATES)
                self._material_costs = config.get("material_costs", self.DEFAULT_MATERIAL_COSTS)
                self._material_lead_times = config.get(
                    "material_lead_times", self.DEFAULT_MATERIAL_LEAD_TIMES
                )
        else:
            self._labor_rates = self.DEFAULT_LABOR_RATES.copy()
            self._material_costs = self.DEFAULT_MATERIAL_COSTS.copy()
            self._material_lead_times = self.DEFAULT_MATERIAL_LEAD_TIMES.copy()

    def estimate(
        self,
        duration_minutes: int,
        role: str,
        materials: Optional[list[str]] = None
    ) -> tuple[float, int]:
        """
        Estimate cost and lead time for a task.

        Args:
            duration_minutes: Estimated task duration in minutes
            role: Role/position responsible for the task
            materials: Optional list of required materials

        Returns:
            Tuple of (total_cost_usd, lead_time_days)
        """
        # Calculate labor cost
        hourly_rate = self._labor_rates.get(role, self._labor_rates.get("general_worker", 35.00))
        labor_cost = (duration_minutes / 60.0) * hourly_rate

        # Calculate material cost and lead time
        material_cost = 0.0
        material_lead_time = 0

        if materials:
            for material in materials:
                material_cost += self._material_costs.get(material, 50.00)  # Default $50
                material_lead_time = max(
                    material_lead_time,
                    self._material_lead_times.get(material, 1)
                )

        # Total cost
        total_cost = labor_cost + material_cost

        # Lead time = base + material procurement + task execution
        # Assume task execution can happen on the last day of material lead time
        task_days = max(1, duration_minutes // (8 * 60))  # 8-hour days
        lead_time = max(self.BASE_LEAD_TIME, material_lead_time) + task_days - 1

        return round(total_cost, 2), lead_time

    def get_labor_rate(self, role: str) -> float:
        """
        Get the hourly labor rate for a role.

        Args:
            role: Role/position identifier

        Returns:
            Hourly rate in USD
        """
        return self._labor_rates.get(role, self._labor_rates.get("general_worker", 35.00))

    def get_material_cost(self, material: str) -> float:
        """
        Get the cost of a material item.

        Args:
            material: Material identifier

        Returns:
            Cost in USD
        """
        return self._material_costs.get(material, 50.00)

    def get_available_roles(self) -> list[str]:
        """
        Get list of available roles.

        Returns:
            List of role identifiers
        """
        return list(self._labor_rates.keys())

    def get_available_materials(self) -> list[str]:
        """
        Get list of available materials.

        Returns:
            List of material identifiers
        """
        return list(self._material_costs.keys())
