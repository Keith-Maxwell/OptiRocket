import json

import numpy as np

from library import orbit_lib as lib


class OptiRocket:
    def __init__(self):
        self.available_propellants = {
            "RP1": {"stages": [1, 2, 3], "ISP": 330, "mean_ISP": 287, "struc_index": 0.15},
            "LH2": {"stages": [2, 3], "ISP": 440, "mean_ISP": None, "struc_index": 0.22},
            "SOLID": {"stages": [1], "ISP": 300, "mean_ISP": 260, "struc_index": 0.10},
        }
        self.masses_limits = {}

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

    def compute_requirements(self):
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

    def __get_propellant_specs(self, stages):
        isp = []
        k = []
        for i, prop in enumerate(stages):
            isp.append(self.available_propellants[prop.upper()]["mean_ISP" if i == 0 else "ISP"])
            k.append(self.available_propellants[prop.upper()]["struc_index"])
        return isp, k

    def _check_propellant_config(self, propellant_config):
        """Checks if the config provided is valid.

        Args:
            propellant_config (List[str]): Ordered list of the propellant names.
            First item is the first stage.

        Returns:
            bool: True -> OK, False -> NOK
        """
        for i, prop in enumerate(propellant_config, start=1):
            if i not in self.available_propellants[prop.upper()]["stages"]:
                print(f"{prop.upper()} cannot be used for stage {i}")
                return False
        return True

    def stage_optimization(self, stages, starting_b_value=1, step=0.0001):
        if self._check_propellant_config(stages) is False:
            raise Exception("Invalid stage configuration. Check the validity of the propellants.")
        n = len(stages)
        ISP, k = self.__get_propellant_specs(stages)
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

        self.b[n - 1] = starting_b_value
        while True:
            self.dV[n - 1] = lib.const.EARTH_GRAV_SEA_LVL * ISP[n - 1] * np.log(self.b[n - 1])
            for j in range(n - 2, -1, -1):
                self.b[j] = (
                    1
                    / self.Omega[j]
                    * (1 - ISP[j + 1] / ISP[j] * (1 - self.Omega[j + 1] * self.b[j + 1]))
                )
                self.dV[j] = lib.const.EARTH_GRAV_SEA_LVL * ISP[j] * np.log(self.b[j])

            if sum(self.dV) <= self.required_dVp:  # not good, continue
                self.b[n - 1] += step
            else:  # good, calculate masses
                for i in range(n - 1, -1, -1):
                    self.a[i] = (1 + k[i]) / self.b[i] - k[i]
                    self.M[i] = self.M[i + 1] / self.a[i]
                    self.m_e[i] = self.M[i] * (1 - self.a[i]) / (1 + k[i])
                    self.m_s[i] = k[i] * self.m_e[i]
                    self.m_stage[i] = self.m_e[i] + self.m_s[i]

                if self._check_masses() is False:
                    # Conditions are not fulfilled
                    self.b[n - 1] += step
                    continue
                else:
                    # Conditions are fulfilled
                    break

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

    def _check_masses(self):
        """Verifies the masses correspond to the limits. Returns True if no limits have been set

        Returns:
            bool: whether the mass is in the limits or not
        """
        check = True
        for i in range(len(self.m_stage)):
            try:
                if (
                    self.m_s[i] > self.masses_limits[i + 1]["max"]
                    or self.m_s[i] < self.masses_limits[i + 1]["min"]
                    or self.m_stage[i] < sum(self.m_stage[i + 1 :]) + self.mission_m_payload
                ):
                    check = False
            except KeyError:  # if a stage limit is not defined, just ignore
                continue
        try:
            if self.M[0] > self.max_total_mass:
                check = False
        except AttributeError:  # if max_total_mass is not defined, just ignore
            pass
        return check


if __name__ == "__main__":

    rocket = OptiRocket()
    rocket.mission(filename="optirocket/missions/POLARsat.json")
    rocket.compute_requirements()
    rocket.add_available_propellant("Hydrazine", [2, 3], 290, 240, 0.15)
    rocket.set_masses_limits(1, 500, 100000)
    rocket.set_masses_limits(2, 200, 80000)
    rocket.set_masses_limits(3, 200, 50000)
    rocket.stage_optimization(["RP1", "RP1", "LH2"])

    print("OK")
