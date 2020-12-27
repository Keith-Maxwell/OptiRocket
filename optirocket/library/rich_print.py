from rich.console import Console
from rich.table import Table

console = Console()


class Results_table:
    def __init__(self, max_n_stages):
        self.console = Console()
        self.table = Table(show_header=True, header_style="bold blue")
        self.table.add_column("Total mass (kg)", justify="right")
        self.table.add_column("Delta V (ms)", justify="right")
        for i in range(max_n_stages):
            self.table.add_column(f"Stage {i+1}")

    def add_results_row(self, stages, total_mass, deltaV, best: bool = False):
        self.table.add_row(
            str(round(total_mass, 1)),
            str(round(sum(deltaV))),
            *stages,
            style="green" if best else None,
        )

    def print(self):
        console.print(self.table)
