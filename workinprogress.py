import importlib
import library.orbit_lib as lib


class OptiRocket():

    def mission(self, filename: str = None, client_name: str = None, altitude_perigee: int = None, altitude_apogee: int = None, inclination: float = None, mass_payload: float = None, launchpad: str = None, launchpad_latitude: float = None):

        # required_keys = set(
        #   ["altitude_perigee", "altitude_apogee", "inclination", "mass_payload", "launchpad_latitude"])

        if filename != None:
            data = importlib.import_module(filename)
            self.client_name = data.client_name
            self.mission_Z_p = data.Z_p
            self.mission_Z_a = data.Z_a
            self.mission_inc = data.inc
            self.mission_m_payload = data.m_payload
            self.mission_launchpad = data.launchpad
            self.mission_launchpad_latitude = data.launchpad_latitude

        else:
            self.client_name = client_name
            self.mission_Z_p = altitude_perigee
            self.mission_Z_a = altitude_apogee
            self.mission_inc = inclination
            self.mission_m_payload = mass_payload
            self.mission_launchpad = launchpad
            self.mission_launchpad_latitude = launchpad_latitude

        necessary_attributes = [self.mission_Z_p, self.mission_Z_a,
                                self.mission_inc, self.mission_m_payload, self.mission_launchpad_latitude]
        if any(attribute == None for attribute in necessary_attributes):
            raise AttributeError(
                "One or more necessary argument is not defined")

    def compute_requirements(self):

        # Calculate the azimuth (in radians)
        self.azimuth = lib.get_azimuth(
            self.mission_inc, self.mission_launchpad_latitude)

        # orbit velocity (m/s)
        self.V_final = lib.get_orbit_velocity(
            self.mission_Z_p, self.mission_Z_a)

        # Initial velocity due to Earth Rotation (m/s)
        self.V_init = lib.get_initial_velocity(
            self.mission_launchpad_latitude, self.azimuth)

        # Delta V losses due to atmospheric drag and more (m/s)
        self.V_losses = lib.get_deltaV_losses(self.mission_Z_p)

        # Propulsive dV required to get to the desired orbit (m/s)
        self.required_dVp = self.V_final - self.V_init + self.V_losses

    def print_requirements(self):
        pass

    def set_available_propellants(self):
        pass


rocket = OptiRocket()
rocket.mission(filename="missions.mission2")
rocket.compute_requirements()
print(rocket.azimuth)
