# /// script
# requires-python = ">=3.10"
# dependencies = ["rich"]
# ///
import argparse
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def get_service_info(label: str) -> dict:
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.splitlines():
            if label in line:
                parts = line.split()
                return {
                    "loaded": True,
                    "pid": parts[0] if parts[0] != "-" else None,
                    "exit_code": parts[1],
                    "label": parts[2],
                }
    except Exception:
        pass
    return {"loaded": False, "pid": None, "exit_code": None, "label": label}


def print_status(label: str, stdout_log: str, stderr_log: str):
    console = Console()
    info = get_service_info(label)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("key", style="bold")
    table.add_column("value")

    if not info["loaded"]:
        table.add_row("State", "[red]✘ not loaded[/red]")
    elif info["pid"]:
        table.add_row("State", "[green]✔ running[/green]")
        table.add_row("PID", f"[bold]{info['pid']}[/bold]")
    else:
        table.add_row("State", "[yellow]✘ not running[/yellow]")

    if info["exit_code"] is not None:
        style = "green" if info["exit_code"] == "0" else "red"
        table.add_row("Exit code", f"[{style}]{info['exit_code']}[/{style}]")

    table.add_row("", "")
    table.add_row("stdout", f"[dim]{stdout_log}[/dim]")
    table.add_row("stderr", f"[dim]{stderr_log}[/dim]")

    console.print()
    console.print(Panel(table, title=f"[bold cyan]{label}[/bold cyan]", border_style="cyan", expand=False))
    console.print()


def main():
    parser = argparse.ArgumentParser(description="Show launchd service status")
    parser.add_argument("--label", required=True, help="launchd service label")
    parser.add_argument("--stdout-log", required=True, help="path to stdout log file")
    parser.add_argument("--stderr-log", required=True, help="path to stderr log file")
    args = parser.parse_args()

    print_status(args.label, args.stdout_log, args.stderr_log)


if __name__ == "__main__":
    main()
