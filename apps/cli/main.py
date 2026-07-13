import asyncio
from pathlib import Path

import typer
from blueprints.executor import BlueprintExecutor
from blueprints.loader import BlueprintLoader
from blueprints.planner import ExecutionPlanner
from orchestrator.scheduler import Scheduler
from rich.console import Console
from rich.table import Table

app = typer.Typer()
blueprint_app = typer.Typer(help="Manage and execute infrastructure blueprints.")
app.add_typer(blueprint_app, name="blueprint")

console = Console()


@app.command()
def version():
    print("STARCORE Platform 0.1.0-dev")


@app.command()
def health():
    print("System OK")


@blueprint_app.command("plan")
def blueprint_plan(path: Path = typer.Argument(..., help="Path to a blueprint YAML file.")):
    """Show the execution plan for a blueprint without running it."""
    blueprint = BlueprintLoader.load(path)
    plan = ExecutionPlanner().create_plan(blueprint)

    table = Table(title=f"Plan for '{blueprint.name}' (v{blueprint.version})")
    table.add_column("Resource")
    table.add_column("Provider")
    table.add_column("Kind")

    for step in plan:
        table.add_row(step["resource"], step["provider"], step["kind"])

    console.print(table)


@blueprint_app.command("run")
def blueprint_run(
    path: Path = typer.Argument(..., help="Path to a blueprint YAML file."),
    parallel: bool = typer.Option(
        False,
        "--parallel",
        help="Execute independent resources concurrently via the dependency-aware Scheduler.",
    ),
):
    """Execute a blueprint against its configured providers."""
    blueprint = BlueprintLoader.load(path)

    if parallel:
        graph = ExecutionPlanner().create_graph(blueprint)
        tasks = asyncio.run(Scheduler().execute(graph))
    else:
        tasks = asyncio.run(BlueprintExecutor().execute(blueprint))

    table = Table(title=f"Result for '{blueprint.name}' (v{blueprint.version})")
    table.add_column("Resource")
    table.add_column("Provider")
    table.add_column("Status")

    status_colors = {
        "success": "green",
        "failed": "red",
        "skipped": "yellow",
        "running": "cyan",
        "pending": "white",
    }

    failed = False
    for task in tasks:
        color = status_colors.get(task.status.value, "white")
        table.add_row(task.resource, task.provider, f"[{color}]{task.status.value}[/{color}]")
        if task.status.value == "failed":
            failed = True

    console.print(table)

    if failed:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
