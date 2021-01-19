import pytest
from optirocket import mainscript as script
from optirocket.library import orbit_lib as lib

rocket = script.OptiRocket()


def test_init():
    rocket.mission("optirocket/missions/ISScargo.json")
    assert rocket.client_name == "Roscosmos"
    assert rocket.mission_m_payload == 32000
    with pytest.raises(AttributeError):
        rocket.mission(client_name="NASA", altitude_perigee=310)


def test_requirements():
    rocket.mission(filename="optirocket/missions/POLARsat.json")
    rocket.compute_requirements()
    assert round(rocket.azimuth, 10) == 0
    rocket.mission(filename="optirocket/missions/ISScargo.json")
    rocket.compute_requirements()
    assert round(rocket.azimuth, 1) == 62.6
    rocket.compute_requirements(DV_losses=1200)
    assert rocket.V_losses == 1200


def test_get_azimuth():
    assert lib.get_azimuth(0, 0) == 90
    assert round(lib.get_azimuth(90, 0)) == 0
    assert round(lib.get_azimuth(90, 57)) == 0
    assert round(lib.get_azimuth(51.6, 45.6), 2) == 62.6


def test_get_deltaV_losses():
    assert lib.get_deltaV_losses(0) == 1387.50
    assert round(lib.get_deltaV_losses(410), 2) == 2230.59


def test_check_masses_inf():
    rocket.mission_m_payload = 100
    rocket.m_s = [1000, 400, 100]
    rocket.m_stage = [10000, 4000, 1000]
    rocket.M = [15100]
    rocket.max_total_mass = 20000
    rocket.masses_limits = {1: {"min": 500, "max": 2000}, 2: {"min": 150, "max": 1000}}
    assert rocket._check_masses_inf() is True
    rocket.masses_limits[3] = {"min": 50, "max": 200}
    assert rocket._check_masses_inf() is True
    rocket.m_s = [400, 400, 100]
    assert rocket._check_masses_inf() is False
    rocket.m_s = [1000, 400, 100]
    rocket.m_stage = [5000, 4000, 1000]
    assert rocket._check_masses_inf() is False


def test_check_masses_sup():
    a = script.OptiRocket()
    a.mission("ISScargo")
    a.compute_requirements()
    a.stage_optimization(["RP1", "RP1", "LH2"])
    assert a.M[0] < 0
    a.set_masses_limits(1, 500, 100000)
    a.set_masses_limits(2, 200, 80000)
    a.set_masses_limits(3, 200, 50000)
    a.set_max_total_mass(1500000)
    a.stage_optimization(["RP1", "RP1"])
    assert a.M[0] == float("inf")


def test_check_propellant_config():
    assert rocket._check_propellant_config(["LH2", "RP1"]) is False
    assert rocket._check_propellant_config(["RP1", "RP1"]) is True
    assert rocket._check_propellant_config(["SOLID", "RP1"]) is True
    assert rocket._check_propellant_config(["solid", "rp1"]) is True
    assert rocket._check_propellant_config(["solid", "SOLID"]) is False
    rocket.add_available_propellant("Hydrazine", [2, 3], 290, 240, 0.15)
    assert rocket._check_propellant_config(["solid", "hydrazine"]) is True
