import numpy as np
import library.constants as const


def get_azimuth(inclination: float, launchpad_latitude: float) -> float:
    """ Returns the launch azimuth (in degrees) given the inclination of the orbit (in degrees) and the latitude of the launchpad (in degrees) """
    return np.degrees(np.arcsin(np.cos(np.radians(inclination)) / np.cos(np.radians(launchpad_latitude))))


def get_deltaV_losses(aim_altitude: float) -> float:
    """ Returns the approximate delta V losses for a launch from ground to aim_altitude
    - aim_altitude : altitude in km"""
    return (2.452e-3) * aim_altitude**2 + 1.051 * aim_altitude + 1387.50


def get_orbit_velocity(perigee: float, apogee: float) -> float:
    """ Returns the velocity at perigee for the specified altitudes (in km)"""
    a = (const.EARTH_RADIUS + (perigee + apogee)/2)
    return np.sqrt(const.EARTH_GRAV_CONST * (2 / (const.EARTH_RADIUS + perigee) - 1 / a)) * 10**3


def get_initial_velocity(launchpad_latitude: float, azimuth: float) -> float:
    """ Returns the initial velocity given by the rotation of the Earth. Depends on the launchpad_latitude (in degrees) and the launch azimuth (in degrees)"""
    return const.EARTH_ROT_RATE * (const.EARTH_RADIUS) * 10**3 * np.cos(np.radians(
        launchpad_latitude)) * np.sin(np.radians(azimuth))
