import asyncio
from pathlib import Path

import typer
from blueprints.executor import BlueprintExecutor
from blueprints.loader import BlueprintLoader
from blueprints.planner import ExecutionPlanner
from core.database import get_session
from core.repository import get_run, list_runs, save_run
from orchestrator.scheduler import Scheduler
from rich.console import Console
from rich.table import Table

app = typer.Typer()
blueprint_app = typer.Typer(help="Manage and execute infrastructure blueprints.")
app.add_typer(blueprint_app, name="blueprint")
runs_app = typer.Typer(help="Inspect persisted blueprint run history.")
app.add_typer(runs_app, name="runs")

console = Console()

STATUS_COLORS = {
    "success": "green",
    "failed": "red",
    "skipped": "yellow",
    "running": "cyan",
    "pending": "white",
}


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

    session = get_session()
    try:
        record = save_run(session, blueprint.name, blueprint.version, parallel, tasks)
        run_id = record.id
    finally:
        session.close()

    table = Table(title=f"Result for '{blueprint.name}' (v{blueprint.version})")
    table.add_column("Resource")
    table.add_column("Provider")
    table.add_column("Status")

    failed = False
    for task in tasks:
        color = STATUS_COLORS.get(task.status.value, "white")
        table.add_row(task.resource, task.provider, f"[{color}]{task.status.value}[/{color}]")
        if task.status.value == "failed":
            failed = True

    console.print(table)
    console.print(f"Run ID: [bold]{run_id}[/bold]")

    if failed:
        raise typer.Exit(code=1)


@runs_app.command("list")
def runs_list():
    """List persisted blueprint run history."""
    session = get_session()
    try:
        records = list_runs(session)
        rows = []
        for record in records:
            counts: dict[str, int] = {}
            for task in record.tasks:
                counts[task.status] = counts.get(task.status, 0) + 1
            summary = ", ".join(f"{count} {status}" for status, count in counts.items())
            rows.append(
                (
                    record.id,
                    record.blueprint_name,
                    record.version,
                    "parallel" if record.parallel else "sequential",
                    record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    summary or "-",
                )
            )
    finally:
        session.close()

    table = Table(title="Blueprint Run History")
    table.add_column("Run ID")
    table.add_column("Blueprint")
    table.add_column("Version")
    table.add_column("Mode")
    table.add_column("Created At")
    table.add_column("Tasks")

    for row in rows:
        table.add_row(*row)

    console.print(table)


@runs_app.command("show")
def runs_show(run_id: str = typer.Argument(..., help="Run ID to inspect.")):
    """Show details of a single persisted blueprint run."""
    session = get_session()
    try:
        record = get_run(session, run_id)
        if record is None:
            header = None
            task_rows = []
        else:
            header = (
                record.blueprint_name,
                record.version,
                record.parallel,
                record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
            task_rows = [
                (
                    task.resource,
                    task.provider,
                    task.status,
                    str(task.result) if task.result else "-",
                )
                for task in record.tasks
            ]
    finally:
        session.close()

    if header is None:
        console.print(f"[red]Run '{run_id}' not found[/red]")
        raise typer.Exit(code=1)

    name, version, parallel, created_at = header
    console.print(
        f"[bold]{name}[/bold] (v{version}) - "
        f"{'parallel' if parallel else 'sequential'} - {created_at}"
    )

    table = Table(title=f"Tasks for run {run_id}")
    table.add_column("Resource")
    table.add_column("Provider")
    table.add_column("Status")
    table.add_column("Result")

    for resource, provider, status, result in task_rows:
        color = STATUS_COLORS.get(status, "white")
        table.add_row(resource, provider, f"[{color}]{status}[/{color}]", result)

    console.print(table)


if __name__ == "__main__":
    app()
