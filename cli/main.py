"""
CLI entry point for the safety agent PoC.

Provides commands to:
- Run observations through the pipeline
- Display results in human-readable format
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safety_agent.schemas import (
    Observation,
    ObservationPotential,
    ObservationType,
)
from safety_agent.orchestrator import run_observation_pipeline, PipelineResult

app = typer.Typer(
    name="safety-agent",
    help="AI-driven safety observation workflow PoC",
    add_completion=False,
)
console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def display_result(result: PipelineResult) -> None:
    """Display pipeline results in a formatted way."""
    console.print()

    # Header
    status = "[green]✓ SUCCESS[/green]" if result.success else "[red]✗ FAILED[/red]"
    console.print(Panel(f"Pipeline Result: {status}", title="Safety Agent PoC"))

    # Observation summary
    console.print("\n[bold]📋 Observation:[/bold]")
    console.print(f"  ID: {result.observation.id}")
    console.print(f"  Site: {result.observation.site}")
    console.print(f"  Type: {result.observation.type.value}")
    console.print(f"  Potential: {result.observation.potential.value}")
    console.print(f"  Description: {result.observation.description[:100]}...")

    # Hazards
    console.print(f"\n[bold]⚠️  Hazards Detected ({len(result.hazards)}):[/bold]")
    if result.hazards:
        hazard_table = Table(show_header=True)
        hazard_table.add_column("ID", style="dim")
        hazard_table.add_column("Type")
        hazard_table.add_column("Taxonomy Ref")
        hazard_table.add_column("Confidence")

        for hazard in result.hazards:
            hazard_table.add_row(
                hazard.hazard_id[:8],
                hazard.type,
                hazard.taxonomy_ref,
                f"{hazard.confidence:.0%}",
            )
        console.print(hazard_table)

    # Scored Hazards
    console.print(f"\n[bold]📊 Risk Scores ({len(result.scored_hazards)}):[/bold]")
    if result.scored_hazards:
        score_table = Table(show_header=True)
        score_table.add_column("Hazard ID", style="dim")
        score_table.add_column("Severity")
        score_table.add_column("Likelihood")
        score_table.add_column("RPN")
        score_table.add_column("Priority")
        score_table.add_column("Due By")

        for scored in result.scored_hazards:
            priority_color = {
                "CRITICAL": "red",
                "HIGH": "yellow",
                "MEDIUM": "blue",
                "LOW": "green",
            }.get(scored.priority.value, "white")

            score_table.add_row(
                scored.hazard_id[:8],
                str(scored.severity),
                str(scored.likelihood),
                str(scored.rpn),
                f"[{priority_color}]{scored.priority.value}[/{priority_color}]",
                scored.due_by.strftime("%Y-%m-%d"),
            )
        console.print(score_table)

    # Action Plans
    console.print(f"\n[bold]📝 Action Plans ({len(result.action_plans)}):[/bold]")
    if result.action_plans:
        for plan in result.action_plans:
            tree = Tree(f"[bold]Plan {plan.plan_id[:8]}[/bold]")
            tree.add(f"Cost: ${plan.cost_estimate_usd:.2f}")
            tree.add(f"Lead Time: {plan.lead_time_days} days")

            if plan.standards_refs:
                standards = tree.add("Standards")
                for ref in plan.standards_refs[:3]:  # Limit to first 3
                    standards.add(ref)

            tasks_branch = tree.add(f"Tasks ({len(plan.tasks)})")
            for task in plan.tasks:
                task_node = tasks_branch.add(f"[cyan]{task.title}[/cyan]")
                task_node.add(f"Control: {task.control_type.value}")
                task_node.add(f"Role: {task.responsible_role}")
                task_node.add(f"Duration: {task.duration_minutes} min")

            console.print(tree)

    # Error if any
    if result.error:
        console.print(f"\n[red]Error: {result.error}[/red]")

    console.print()


@app.command()
def run(
    description: str = typer.Option(
        ...,
        "--description", "-d",
        help="Description of the safety observation"
    ),
    site: str = typer.Option(
        "Default Site",
        "--site", "-s",
        help="Site/location of the observation"
    ),
    potential: ObservationPotential = typer.Option(
        ObservationPotential.NEAR_MISS,
        "--potential", "-p",
        help="Potential severity classification"
    ),
    obs_type: ObservationType = typer.Option(
        ObservationType.UNSAFE_CONDITION,
        "--type", "-t",
        help="Type of observation"
    ),
    observed_at: Optional[str] = typer.Option(
        None,
        "--observed-at",
        help="Observation timestamp (ISO format). Defaults to now."
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON instead of formatted text"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose logging"
    ),
) -> None:
    """
    Run a safety observation through the analysis pipeline.

    Example:
        safety-agent run -d "Scaffolding board slipped" -s "Building A" -p NEAR_MISS
    """
    setup_logging(verbose)

    # Parse observation timestamp
    if observed_at:
        try:
            timestamp = datetime.fromisoformat(observed_at)
        except ValueError:
            console.print(f"[red]Invalid timestamp format: {observed_at}[/red]")
            raise typer.Exit(1)
    else:
        timestamp = datetime.now()

    # Create observation
    observation = Observation(
        observed_at=timestamp,
        site=site,
        potential=potential,
        type=obs_type,
        description=description,
    )

    console.print("[dim]Running observation through pipeline...[/dim]")

    # Run pipeline
    result = run_observation_pipeline(observation)

    # Output result
    if output_json:
        print(result.model_dump_json(indent=2))
    else:
        display_result(result)

    # Exit with appropriate code
    if not result.success:
        raise typer.Exit(1)


@app.command()
def demo() -> None:
    """
    Run a demo observation to test the pipeline.

    Uses a sample scaffolding incident observation.
    """
    console.print("[bold]Running demo observation...[/bold]\n")

    observation = Observation(
        observed_at=datetime.now(),
        site="Building A - 3rd floor",
        potential=ObservationPotential.NEAR_MISS,
        type=ObservationType.UNSAFE_CONDITION,
        description=(
            "Scaffolding board slipped but worker caught it before falling. "
            "The board was not properly secured with toe boards. "
            "Worker was wearing harness but it was not attached."
        ),
        trade_category_id="scaffolding",
        trade_partner_id="partner_001",
    )

    result = run_observation_pipeline(observation)
    display_result(result)


@app.command()
def version() -> None:
    """Show version information."""
    from safety_agent import __version__
    console.print(f"Safety Agent PoC v{__version__}")


if __name__ == "__main__":
    app()
