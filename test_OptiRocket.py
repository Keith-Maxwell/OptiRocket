import workinprogress as script
import library.orbit_lib as lib

import pytest


rocket = script.OptiRocket()


def test_init():
    rocket.mission("missions.mission1")
    assert rocket.client_name == "Roscosmos"
    assert rocket.mission_m_payload == 32000
    with pytest.raises(AttributeError):
        rocket.mission(client_name="NASA", altitude_perigee=310)


def test_requirements():
    rocket.mission(filename="missions.mission2")
    rocket.compute_requirements()
    assert round(rocket.azimuth, 10) == 0
    rocket.mission(filename="missions.mission1")
    rocket.compute_requirements()
    assert round(rocket.azimuth, 1) == 62.6


def test_get_azimuth():
    assert lib.get_azimuth(0, 0) == 90
    assert round(lib.get_azimuth(90, 0)) == 0
    assert round(lib.get_azimuth(90, 57)) == 0
    assert round(lib.get_azimuth(51.6, 45.6), 2) == 62.6


def test_get_deltaV_losses():
    assert lib.get_deltaV_losses(0) == 1387.50
    assert round(lib.get_deltaV_losses(410), 2) == 2230.59
