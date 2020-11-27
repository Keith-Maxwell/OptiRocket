import numpy as np
import library.constants as const


def get_azimuth(inclination: float, launchpad_latitude: float) -> float:
    """Gets the required Azimuth of the launch in order to satisfy the orbit inclination.
    The azimuth changes in function of the targeted orbit as well as the position of the launchpad.

    Args:
        inclination (float): inclination (in degrees) of the targeted orbital plane compared to the equatorial plane.
        launchpad_latitude (float): latitude of the chosen launchpad (in degrees).

    Returns:
        float: Azimuth of the launch.
    """
    return np.degrees(np.arcsin(np.cos(np.radians(inclination)) / np.cos(np.radians(launchpad_latitude))))


def get_deltaV_losses(aim_altitude: float) -> float:
    """Estimates the losses due to various sources, including atmospheric drag, using a very simplified equation.
    The result is the amount of Delta V (ie: the velocity) lost during ascent of the rocket.

    Args:
        aim_altitude (float): The altitude of the perigee/injection in km

    Returns:
        float: the velocity lost during ascent in m/s
    """
    return (2.452e-3) * aim_altitude**2 + 1.051 * aim_altitude + 1387.50


def get_orbit_velocity(perigee: float, apogee: float) -> float:
    """Gives the orbital velocity at a given altitude. Used for computing the minimal required velocity to get to orbit.
    This velocity depends only on the shape of the orbit : its apogee and perigee. The result is the velocity at perigee.

    Args:
        perigee (float): Altitude of the lowest point of the orbit (in km)
        apogee (float): Altitude of the highest point of the orbit (in km) 

    Returns:
        float: Orbital velocity at perigee
    """
    a = (const.EARTH_RADIUS + (perigee + apogee)/2)
    return np.sqrt(const.EARTH_GRAV_CONST * (2 / (const.EARTH_RADIUS + perigee) - 1 / a)) * 10**3


def get_initial_velocity(launchpad_latitude: float, azimuth: float) -> float:
    """The Earth rotates on itself, and provides an initial velocity to rockets.
    This initial velocity helps the rockets if they launch in same way the planet rotates, 
    or slows the rocket if it is launched the other way.
    This function returns the initial velocity, positive or negative, 
    depending on the position of the launchpad and the azimuth of the launch.

    Args:
        launchpad_latitude (float): Latitude (in degrees) of the launchpad
        azimuth (float): Azimuth (in degrees) of the launch. The direction in which the rocket goes.

    Returns:
        float: Initial velocity (in m/s) that the rocket gets from Earth rotation. Can be positive or negative.
    """
    return const.EARTH_ROT_RATE * (const.EARTH_RADIUS) * 10**3 * np.cos(np.radians(
        launchpad_latitude)) * np.sin(np.radians(azimuth))
