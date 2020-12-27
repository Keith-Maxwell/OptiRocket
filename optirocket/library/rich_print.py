from rich import print as rprint
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
            str(round(sum(deltaV), 1)),
            *stages,
            style="green"
            if best
            else "red"
            if sum(deltaV) == float("inf") or total_mass < 0
            else None,
        )

    def print(self):
        console.print(self.table)


def mission_requirements(rocket):
    console.rule("Mission Recap")
    rprint(f"The rocket will launch a {rocket.mission_m_payload} kg payload")
    rprint(
        "The targeted orbit is",
        f"a {rocket.mission_Z_p}/{rocket.mission_Z_a} km ellipse"
        if rocket.mission_Z_a != rocket.mission_Z_p
        else f"circular at {rocket.mission_Z_p} km",
    )
    rprint(f"The final velocity in orbit is {round(rocket.V_final, 2)} m/s")
    rprint(
        f"Due to the {rocket.mission_inc}° inclination of the desired orbit, the rocket must be launched at a {round(rocket.azimuth,1)}° azimuth. "
    )
    rprint(
        f"This will result in {round(rocket.V_init,2)} m/s velocity gains from the Earth rotation "
    )
    rprint(f"Atmospheric losses are estimated at {round(rocket.V_losses, 2)} m/s.")
    rprint(f"The propulsive Delta V required is {round(rocket.required_dVp, 2)} m/s\n\n")
    console.rule("Optimization")
