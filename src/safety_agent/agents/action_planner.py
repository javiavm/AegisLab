"""
Action Planner Agent - Generates corrective action plans.

Responsibilities:
- Generate corrective tasks following hierarchy of controls using LLM
- Reference applicable safety standards (OSHA, ISO 45001)
- Estimate costs and lead times via ResourcePlanner tool
"""

import logging
from typing import Any

from safety_agent.agents.base import BaseAgent, AgentError
from safety_agent.llm.client import LLMClient
from safety_agent.schemas import ScoredHazard, ActionPlan, Task, ControlHierarchy, Hazard
from safety_agent.tools.standards_lookup import StandardsLookup
from safety_agent.tools.resource_planner import ResourcePlanner

logger = logging.getLogger(__name__)


class ActionPlannerAgent(BaseAgent[list[ScoredHazard], list[ActionPlan]]):
    """
    Agent that generates corrective action plans using LLM.

    Uses LLM to:
    - Generate appropriate corrective tasks
    - Apply hierarchy of controls principle
    - Define acceptance criteria

    Uses tools:
    - StandardsLookup: Find applicable OSHA/ISO 45001 clauses
    - ResourcePlanner: Calculate cost and lead time estimates

    Input: list[ScoredHazard]
    Output: list[ActionPlan]
    """

    name = "ActionPlannerAgent"

    SYSTEM_PROMPT = """You are a safety action planning expert. Your job is to create corrective action plans for identified hazards.

You follow the HIERARCHY OF CONTROLS (in order of effectiveness):
1. ELIMINATION - Physically remove the hazard entirely
2. SUBSTITUTION - Replace with something less hazardous
3. ENGINEERING - Isolate people from the hazard (guards, barriers, ventilation)
4. ADMINISTRATIVE - Change the way people work (procedures, training, signage, scheduling)
5. PPE - Personal protective equipment (last resort)

When creating action plans:
1. Prioritize higher-level controls when feasible
2. Include specific, actionable tasks
3. Define clear acceptance criteria for each task
4. Consider practical implementation constraints
5. Assign appropriate responsible roles

Available roles: safety_engineer, safety_officer, supervisor, scaffolder, electrician, general_worker, contractor

Available materials: safety_barriers, warning_signs, toe_boards, fixings, training_materials, ppe_checklist, hard_hat, safety_glasses, safety_harness, fire_extinguisher, first_aid_kit, lockout_tagout_kit, respirator, chemical_gloves, spill_kit

Output valid JSON only."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        hazard_context: dict[str, Hazard] | None = None
    ):
        """
        Initialize the Action Planner Agent.

        Args:
            llm_client: Optional LLM client for task generation
            hazard_context: Optional mapping of hazard_id to original Hazard objects
        """
        super().__init__(llm_client)
        self.standards_lookup = StandardsLookup()
        self.resource_planner = ResourcePlanner()
        self.hazard_context = hazard_context or {}

    def set_hazard_context(self, hazards: list[Hazard]) -> None:
        """
        Set the hazard context for looking up original hazard details.

        Args:
            hazards: List of original Hazard objects
        """
        self.hazard_context = {h.hazard_id: h for h in hazards}

    def run(self, scored_hazards: list[ScoredHazard]) -> list[ActionPlan]:
        """
        Generate action plans for scored hazards using LLM.

        Args:
            scored_hazards: List of hazards with risk scores

        Returns:
            List of action plans with tasks, costs, and timelines

        Raises:
            AgentError: If plan generation fails
        """
        try:
            plans = []

            for scored_hazard in scored_hazards:
                plan = self._generate_plan(scored_hazard)
                plans.append(plan)

            logger.info(f"Action Planner generated {len(plans)} action plans")
            return plans

        except Exception as e:
            logger.error(f"Action Planner failed: {e}", exc_info=True)
            raise AgentError(self.name, f"Failed to generate action plans: {e}") from e

    def _generate_plan(self, scored_hazard: ScoredHazard) -> ActionPlan:
        """
        Generate an action plan for a single hazard using LLM.

        Args:
            scored_hazard: Scored hazard to plan for

        Returns:
            ActionPlan with tasks and resource estimates
        """
        # Get original hazard details if available
        original_hazard = self.hazard_context.get(scored_hazard.hazard_id)
        hazard_type = original_hazard.type if original_hazard else "general_safety"
        hazard_description = original_hazard.description if original_hazard else "Safety hazard"
        taxonomy_ref = original_hazard.taxonomy_ref if original_hazard else "HAZ-GEN-001"

        # Step 1: Look up applicable standards
        standards = self.standards_lookup.get_standards_for_hazard(taxonomy_ref)

        # Step 2: Generate tasks using LLM
        prompt = self._build_prompt(scored_hazard, hazard_type, hazard_description, standards)
        raw_tasks = self.llm_client.extract_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT
        )

        logger.info(f"LLM generated {len(raw_tasks) if raw_tasks else 0} tasks for hazard {scored_hazard.hazard_id}")

        # Parse tasks from LLM response
        tasks = self._parse_tasks(raw_tasks, scored_hazard)

        # Step 3: Calculate resources for each task
        total_cost = 0.0
        max_lead_time = 0

        for task in tasks:
            cost, lead_time = self.resource_planner.estimate(
                duration_minutes=task.duration_minutes,
                role=task.responsible_role,
                materials=task.material_requirements,
            )
            total_cost += cost
            max_lead_time = max(max_lead_time, lead_time)

        return ActionPlan(
            hazard_id=scored_hazard.hazard_id,
            tasks=tasks,
            standards_refs=standards[:5],  # Limit to top 5 standards
            cost_estimate_usd=round(total_cost, 2),
            lead_time_days=max_lead_time,
        )

    def _parse_tasks(self, raw_tasks: Any, scored_hazard: ScoredHazard) -> list[Task]:
        """
        Parse LLM response into Task objects.

        Args:
            raw_tasks: Raw LLM response (list of dicts)
            scored_hazard: The hazard being addressed

        Returns:
            List of validated Task objects
        """
        if not raw_tasks or not isinstance(raw_tasks, list):
            logger.warning("LLM returned no tasks, using fallback")
            return self._fallback_tasks(scored_hazard)

        tasks = []
        for raw in raw_tasks:
            try:
                # Parse control type
                control_str = raw.get("control_type", "ADMINISTRATIVE").upper()
                try:
                    control_type = ControlHierarchy(control_str)
                except ValueError:
                    control_type = ControlHierarchy.ADMINISTRATIVE

                # Parse duration
                duration = raw.get("duration_minutes", 60)
                try:
                    duration = int(duration)
                    duration = max(15, min(480, duration))  # Clamp between 15 min and 8 hours
                except (TypeError, ValueError):
                    duration = 60

                # Parse materials
                materials = raw.get("material_requirements", [])
                if not isinstance(materials, list):
                    materials = []
                # Filter to known materials
                known_materials = self.resource_planner.get_available_materials()
                materials = [m for m in materials if m in known_materials]

                # Parse role
                role = raw.get("responsible_role", "safety_officer")
                known_roles = self.resource_planner.get_available_roles()
                if role not in known_roles:
                    role = "safety_officer"

                task = Task(
                    title=raw.get("title", "Corrective action")[:100],
                    description=raw.get("description", "Implement corrective measures")[:500],
                    control_type=control_type,
                    responsible_role=role,
                    duration_minutes=duration,
                    material_requirements=materials,
                    acceptance_criteria=raw.get("acceptance_criteria", "Task completed and verified")[:300],
                )
                tasks.append(task)
            except Exception as e:
                logger.warning(f"Failed to parse task: {e}")
                continue

        # Ensure at least one task
        if not tasks:
            return self._fallback_tasks(scored_hazard)

        return tasks

    def _fallback_tasks(self, scored_hazard: ScoredHazard) -> list[Task]:
        """
        Generate fallback tasks when LLM fails.

        Args:
            scored_hazard: The hazard being addressed

        Returns:
            List of default tasks
        """
        tasks = [
            Task(
                title="Conduct safety assessment",
                description="Perform detailed safety assessment of the hazard area and document findings.",
                control_type=ControlHierarchy.ADMINISTRATIVE,
                responsible_role="safety_officer",
                duration_minutes=60,
                material_requirements=["training_materials"],
                acceptance_criteria="Assessment report completed and reviewed",
            )
        ]

        if scored_hazard.severity >= 3:
            tasks.append(Task(
                title="Implement physical controls",
                description="Install appropriate barriers or safety devices to control the hazard.",
                control_type=ControlHierarchy.ENGINEERING,
                responsible_role="safety_engineer",
                duration_minutes=120,
                material_requirements=["safety_barriers", "warning_signs"],
                acceptance_criteria="Physical controls installed and tested",
            ))

        return tasks

    def _build_prompt(
        self,
        scored_hazard: ScoredHazard,
        hazard_type: str,
        hazard_description: str,
        standards: list[str]
    ) -> str:
        """
        Build the prompt for action plan generation.

        Args:
            scored_hazard: The hazard to plan for
            hazard_type: Type of hazard
            hazard_description: Description of the hazard
            standards: Applicable safety standards

        Returns:
            Formatted prompt for LLM
        """
        standards_text = "\n".join(f"- {s}" for s in standards[:5]) if standards else "- General safety standards apply"

        return f"""Generate a corrective action plan for the following hazard.

HAZARD DETAILS:
- Hazard ID: {scored_hazard.hazard_id}
- Type: {hazard_type}
- Description: {hazard_description}
- Severity: {scored_hazard.severity}/5
- Likelihood: {scored_hazard.likelihood}/5
- Priority: {scored_hazard.priority.value}
- RPN (Risk Priority Number): {scored_hazard.rpn}

APPLICABLE STANDARDS:
{standards_text}

Generate 2-4 corrective action tasks following the hierarchy of controls.
For a hazard with severity {scored_hazard.severity} and priority {scored_hazard.priority.value}, focus on effective controls.

Each task must include:
- title: Short descriptive title (max 100 chars)
- description: Detailed instructions for implementation
- control_type: One of ELIMINATION, SUBSTITUTION, ENGINEERING, ADMINISTRATIVE, PPE
- responsible_role: One of safety_engineer, safety_officer, supervisor, scaffolder, electrician, general_worker, contractor
- duration_minutes: Estimated time (15-480 minutes)
- material_requirements: Array of materials needed (use from: safety_barriers, warning_signs, toe_boards, fixings, training_materials, ppe_checklist, hard_hat, safety_glasses, safety_harness, fire_extinguisher, first_aid_kit, lockout_tagout_kit, respirator, chemical_gloves, spill_kit)
- acceptance_criteria: How to verify task completion

Return a JSON array of tasks:
[
  {{
    "title": "Task title",
    "description": "Detailed description",
    "control_type": "ENGINEERING",
    "responsible_role": "safety_engineer",
    "duration_minutes": 120,
    "material_requirements": ["safety_barriers", "warning_signs"],
    "acceptance_criteria": "Verification criteria"
  }}
]"""
