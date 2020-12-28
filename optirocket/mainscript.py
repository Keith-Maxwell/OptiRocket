import json
import warnings
from importlib import resources

import numpy as np
from rich.progress import track

from optirocket.library import orbit_lib as lib
from optirocket.library import rich_print


class OptiRocket:
    def __init__(self):
        self.available_propellants = {
            "RP1": {"stages": [1, 2, 3], "ISP": 330, "mean_ISP": 287, "struc_index": 0.15},
            "LH2": {"stages": [2, 3], "ISP": 440, "mean_ISP": None, "struc_index": 0.22},
            "SOLID": {"stages": [1], "ISP": 300, "mean_ISP": 260, "struc_index": 0.10},
        }
        self.masses_limits = {}

    def _check_masses_inf(self) -> bool:
        """Verifies the masses correspond to the limits. Returns True if no limits have been set

        Returns:
            bool: whether the mass is in the limits or not
        """
        check = True
        for i in range(len(self.m_stage)):
            try:
                if (
                    self.m_s[i] < self.masses_limits[i + 1]["min"]
                    or self.m_stage[i] < sum(self.m_stage[i + 1 :]) + self.mission_m_payload
                ):
                    check = False
            except KeyError:  # if a stage limit is not defined, just ignore
                continue

        return check

    def _check_masses_sup(self):
        check = True
        for i in range(len(self.m_stage)):
            try:
                if self.m_s[i] > self.masses_limits[i + 1]["max"]:
                    check = False
            except KeyError:  # if a stage limit is not defined, just ignore
                continue
        try:
            if self.M[0] > self.max_total_mass:
                check = False
        except AttributeError:  # if max_total_mass is not defined, just ignore
            pass

        return check

    def _check_propellant_config(self, propellant_config, show_output: bool = True) -> bool:
        """Checks if the config provided is valid.

        Args:
            propellant_config (List[str]): Ordered list of the propellant names.
            First item is the first stage.
            show_output (bool): True will print when a propellant combination cannot be used.

        Returns:
            bool: True -> OK, False -> NOK
        """
        for stage, prop in enumerate(propellant_config, start=1):
            if stage not in self.available_propellants[prop.upper()]["stages"]:
                if show_output is True:
                    print(f"{prop.upper()} cannot be used for stage {stage}")
                return False
        return True

    def _create_combinations(self, min_number_stages: int, max_number_stages: int):
        """Generates all the possible and valid propellant configurations.

        Args:
            min_number_stages (int): Minimum number of stages
            max_number_stages (int): Maximum number of stages

        Returns:
            List: all the possible and valid combinations
        """
        from itertools import product

        props = list(self.available_propellants)
        valid_combinations = []
        for k in range(min_number_stages, max_number_stages + 1):
            combinations = list(product(props, repeat=k))
            for comb in combinations:
                if self._check_propellant_config(comb, show_output=False):
                    valid_combinations.append(comb)
        return valid_combinations

    def _get_propellant_specs(self, stages):
        isp = []
        k = []
        for i, prop in enumerate(stages):
            isp.append(self.available_propellants[prop.upper()]["mean_ISP" if i == 0 else "ISP"])
            k.append(self.available_propellants[prop.upper()]["struc_index"])
        return isp, k

    def mission(
        self,
        filename: str = None,
        client_name: str = None,
        altitude_perigee: int = None,
        altitude_apogee: int = None,
        inclination: float = None,
        mass_payload: float = None,
        launchpad: str = None,
        launchpad_latitude: float = None,
    ):
        """Defines the mission to build the rocket for. Can be defined manually or in a python file.

        Args:
            filename (str, optional): Path/name of the file containing the mission data.
            client_name (str, optional): Name of the mission customer.
            altitude_perigee (int, optional): Altitude in km of the perigee at injection.
            altitude_apogee (int, optional): Altitude in km of the apogee at injection.
            inclination (float, optional): Required orbit inclination.
            mass_payload (float, optional): Mass of the payload. Defaults to None.
            launchpad (str, optional): Name of the launch location.
            launchpad_latitude (float, optional): Latitude in degrees of the launchpad.

        Raises:
            AttributeError: If a necessary attribute is not given, raises an exception.
        """
        if filename is not None:
            if any(filename == f for f in ["POLARsat", "GEOsat", "ISScargo", "LEOsat", "SSOsat"]):
                with resources.open_text("optirocket.missions", filename + ".json") as file:
                    data = json.load(file)
            else:
                with open(filename) as file:
                    data = json.load(file)
            self.client_name = data["client_name"]
            self.mission_Z_p = data["altitude_perigee"]
            self.mission_Z_a = data["altitude_apogee"]
            self.mission_inc = data["inclination"]
            self.mission_m_payload = data["mass_payload"]
            self.mission_launchpad = data["launchpad"]
            self.mission_launchpad_latitude = data["launchpad_latitude"]

        else:
            self.client_name = client_name
            self.mission_Z_p = altitude_perigee
            self.mission_Z_a = altitude_apogee
            self.mission_inc = inclination
            self.mission_m_payload = mass_payload
            self.mission_launchpad = launchpad
            self.mission_launchpad_latitude = launchpad_latitude

        necessary_attributes = {
            "altitude_perigee": self.mission_Z_p,
            "altitude_apogee": self.mission_Z_a,
            "inclination": self.mission_inc,
            "mass_payload": self.mission_m_payload,
            "launchpad_latitude": self.mission_launchpad_latitude,
        }
        for key, value in necessary_attributes.items():
            if value is None:
                raise AttributeError(f"{key} is necessary but is not defined")

    def compute_requirements(self, show_output: bool = False):
        """Calculates the main requirements from the mission profile specified. Determines :
        - azimuth (in degrees),
        - V_final, Orbital velocity at required altitude (in m/s)
        - V_init, Initial velocity due to Earth rotation (in m/s)
        - V_losses, velocity losses due to atmospheric drag (in m/s)
        - required_dVp, Total propulsive DeltaV to reach orbit (in m/s)
        """
        self.azimuth = lib.get_azimuth(self.mission_inc, self.mission_launchpad_latitude)
        self.V_final = lib.get_orbit_velocity(self.mission_Z_p, self.mission_Z_a)
        self.V_init = lib.get_initial_velocity(self.mission_launchpad_latitude, self.azimuth)
        self.V_losses = lib.get_deltaV_losses(self.mission_Z_p)
        self.required_dVp = self.V_final - self.V_init + self.V_losses

        if show_output is True:
            rich_print.mission_requirements(self)

    def set_masses_limits(self, stage: int, min: float, max: float):
        """Sets the lower and upper limits on the structural mass of a stage

        Args:
            stage (int): Number of the stage
            min (float): minimum structural mass in kg
            max (float): maximum structural mass in kg
        """
        self.masses_limits[stage] = {"min": min, "max": max}

    def set_max_total_mass(self, max_total_mass: float):
        """Sets the total maximum mass of the rocket, fully fueled.

        Args:
            max_total_mass (float): Maximum mass of the rocket
        """
        self.max_total_mass = max_total_mass

    def add_available_propellant(
        self, name: str, possible_stages, isp: float, mean_isp: float, structural_index: float
    ):
        """Allows to add a custom propellant to the list of availlable propellants.

        Args:
            name (str): Code name of the propellant
            possible_stages (List[int]): List of the stages where this new propellant can be used
            isp (float): Specific impulse (vacuum)
            mean_isp (float): Mean specific impulse (Atmospheric)
            structural_index (float): Ratio of propellant mass over structural mass
        """
        self.available_propellants[name.upper()] = {
            "stages": possible_stages,
            "ISP": isp,
            "mean_ISP": mean_isp,
            "struc_index": structural_index,
        }

    def stage_optimization(self, stages, precision: float = 0.001, step: float = 0.0001):
        """finds the most optimized rocket configuration using the given stage propellant list.
        A list of n elements will result in a rocket with n stages.

        Args:
            stages (List[str]): List of propellants used stage by stage in order from bottom to top
            precision (float, optional): Error on the Delta V. Defaults to 0.001.
            step (float, optional): Step for increase of coef b when the rocket must satisfy
            masses constraints. Defaults to 0.0001.

        Raises:
            Exception: Invalid stage configuration. Check the validity of the propellants.
        """
        if self._check_propellant_config(stages) is False:
            raise Exception("Invalid stage configuration. Check the validity of the propellants.")
        n = len(stages)
        ISP, k = self._get_propellant_specs(stages)
        self.a = [0] * n
        self.b = [0] * n
        self.dV = [0] * n
        self.M = [0] * n + [self.mission_m_payload]
        self.m_e = [0] * n
        self.m_s = [0] * n
        self.m_stage = [0] * n

        self.Omega = [0] * n
        for i in range(n - 1, -1, -1):
            self.Omega[i] = k[i] / (1 + k[i])

        # ------------- Lagrange Multiplier Method ---------------
        # Setup of a dichotomy method
        low = 0.5
        high = 10
        middle = (low + high) / 2
        self.b[n - 1] = middle
        # --------
        min_deltaV_ok = False  # dichotomy is used until the required Delta V is reached

        while True:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.dV[n - 1] = lib.const.EARTH_GRAV_SEA_LVL * ISP[n - 1] * np.log(self.b[n - 1])
                for j in range(n - 2, -1, -1):
                    self.b[j] = (
                        1
                        / self.Omega[j]
                        * (1 - ISP[j + 1] / ISP[j] * (1 - self.Omega[j + 1] * self.b[j + 1]))
                    )
                    self.dV[j] = lib.const.EARTH_GRAV_SEA_LVL * ISP[j] * np.log(self.b[j])

            if (
                sum(self.dV) - self.required_dVp < -precision and not min_deltaV_ok
            ):  # not good, continue
                low = middle
                middle = (low + high) / 2
                self.b[n - 1] = middle

            elif sum(self.dV) - self.required_dVp > precision and not min_deltaV_ok:
                high = middle
                middle = (low + high) / 2
                self.b[n - 1] = middle

            else:  # good, calculate masses
                min_deltaV_ok = True  # min deltaV reached, adjust in function of the masses.
                for i in range(n - 1, -1, -1):
                    self.a[i] = (1 + k[i]) / self.b[i] - k[i]
                    self.M[i] = self.M[i + 1] / self.a[i]
                    self.m_e[i] = self.M[i] * (1 - self.a[i]) / (1 + k[i])
                    self.m_s[i] = k[i] * self.m_e[i]
                    self.m_stage[i] = self.m_e[i] + self.m_s[i]

                if self._check_masses_inf() is False:
                    # Conditions are not fulfilled
                    # The rocket will diverge from the optimum to satisfy the masses
                    self.b[n - 1] += step
                    continue
                elif self._check_masses_sup() is False:
                    self.m_stage = [float("inf") for i in range(n)]
                    self.M = [float("inf") for i in range(n)]
                    self.m_e = [float("inf") for i in range(n)]
                    self.m_s = [float("inf") for i in range(n)]
                    self.dV = [float("inf") for i in range(n)]
                    break

                else:
                    # Conditions are fulfilled
                    break

    def optimize_best_rocket(
        self,
        min_number_stages: int,
        max_number_stages: int,
        starting_b_value: float = 1,
        step: float = 0.0001,
        show_output: bool = False,
    ):
        combinations = self._create_combinations(min_number_stages, max_number_stages)
        self.best_mass = float("inf")  # Initialize variable
        self.optimization_results = {}

        for stages in track(combinations):

            # call optimization on one combination
            self.stage_optimization(stages, starting_b_value, step)

            self.optimization_results[stages] = {
                "total_mass": self.M[0],
                "struc_mass": self.m_s,
                "fuel_mass": self.m_e,
                "stage_mass": self.m_stage,
                "deltaV": self.dV,
            }

            if 0 < self.M[0] < self.best_mass:
                self.best_mass = self.M[0]
                self.best_stages = stages
                self.best_dV = self.dV
        # TODO : handle error when there is no optimization possible
        if show_output is True:

            results = rich_print.Results_table(max_number_stages)
            for key, value in self.optimization_results.items():
                results.add_results_row(key, value["total_mass"], value["deltaV"])
            results.add_results_row(self.best_stages, self.best_mass, self.best_dV, best=True)
            results.print()
            rich_print.best_rocket_table(
                self.optimization_results, self.best_stages, self.mission_m_payload
            )

    # TODO: Print detailled rocket characteristics
    # def print_best_rocket(self):


if __name__ == "__main__":

    rocket = OptiRocket()
    rocket.mission(filename="ISScargo")
    rocket.compute_requirements(show_output=True)

    # rocket.add_available_propellant("Hydrazine", [2, 3, 4], 290, 240, 0.15)
    rocket.set_masses_limits(1, 500, 100000)
    rocket.set_masses_limits(2, 200, 80000)
    rocket.set_masses_limits(3, 200, 50000)
    rocket.set_max_total_mass(1500000)

    rocket.optimize_best_rocket(min_number_stages=2, max_number_stages=3, show_output=True)
