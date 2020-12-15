from rich.console import Console
from rich.table import Table

console = Console()


def init_results_table(n_stages):
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Total mass (kg)", justify="right")
    for i in range(n_stages):
        table.add_column(f"Stage {i+1}")
    return table


def add_results_row(table, stages, total_mass, best: bool = False):

    table.add_row(str(round(total_mass, 3)), *stages, style="green" if best else None)
    return table


def print_results(table):
    console.print(table)
