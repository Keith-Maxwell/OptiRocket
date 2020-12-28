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
        rprint()
        console.rule("Optimization")
        rprint()
        console.print(self.table)


def mission_requirements(rocket):
    rprint("\n")
    console.rule("Mission Recap")
    rprint()

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


def best_rocket_table(opti_results, combination, payload):
    rprint("\n")
    console.rule("Best rocket parameters")
    rprint()

    table = Table(show_header=True, header_style="bold green")

    table.add_column("", justify="left")
    table.add_column("Delta V (m/s)", justify="center")
    table.add_column("Structural mass (kg)", justify="center")
    table.add_column("Fuel mass (kg)", justify="center")
    table.add_column("Total stage mass (kg)", justify="right")

    for i, e in enumerate(combination):
        table.add_row(
            f"Stage {i+1} : {e}",
            "{:,}".format(round(opti_results[combination]["deltaV"][i], 3)),
            "{:,}".format(round(opti_results[combination]["struc_mass"][i], 3)),
            "{:,}".format(round(opti_results[combination]["fuel_mass"][i], 3)),
            "{:,}".format(round(opti_results[combination]["stage_mass"][i], 3)),
            end_section=True if i == len(combination) - 1 else None,
        )

    table.add_row(
        "Total",
        "{:,}".format(round(sum(opti_results[combination]["deltaV"]), 3)),
        "{:,}".format(round(sum(opti_results[combination]["struc_mass"]), 3)),
        "{:,}".format(round(sum(opti_results[combination]["fuel_mass"]), 3)),
        "{:,}".format(round(sum(opti_results[combination]["stage_mass"]), 3)),
    )

    console.print(table)
    m_tot = opti_results[combination]["total_mass"]
    rprint(
        f"\n Do not forget the mass of the payload at {payload} kg for a grand total of {round(m_tot,3):,} kg \n"
    )
