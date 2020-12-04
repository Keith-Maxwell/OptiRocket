import numpy as np
import importlib

from numpy.core.numeric import Infinity
import library.orbit_lib as lib


# ------------ Definitions ---------------


def Injection_Requirements(mission: str = "mission5"):
    """Calculates the main requirements from the mission profile specified.
    When given a Mission profile in the form of a python file, this function
    calculates the azimuth required for the launch, the final required velocity
    for the given orbit, the initial velocity provided by the Earth, the velocity
    losses due to various sources and finaly the propulsive delta V required
    by the rocket to reach orbit.

    Args:
        mission (str, optional): name of the python file (without extension) 
        that contains the mission data. Defaults to "mission5".

    Returns:
        float: Azimuth of the launch
        float: Orbital velocity required at injection
        float: Initial velocity provided by the Earth rotation
        float: Velocity Losses from reaching the orbit
        float: Total Propulsive Delta V of the Rocket
        float: Mass of the payload
    """

    data = importlib.import_module("missions." + mission)

    # Calculate the azimuth (in radians)
    azi = lib.get_azimuth(data.inc, data.launchpad_latitude)
    # orbit velocity (m/s)
    V_final = lib.get_orbit_velocity(data.Z_p, data.Z_a)
    # Initial velocity due to Earth Rotation (m/s)
    V_init = lib.get_initial_velocity(data.launchpad_latitude, azi)
    # Delta V losses due to atmospheric drag and more (m/s)
    V_losses = lib.get_deltaV_losses(data.Z_p)
    # Propulsive dV required to get to the desired orbit (m/s)
    dVp = V_final - V_init + V_losses
    return azi, V_final, V_init, V_losses, dVp, data.m_payload


def Propellant_spec(prop_type: str, stage_number: int):
    """This function returns the predetermined characteristics
    of rocket fuel. The main characteristics are the ISP, 
    the higher the better, and the structural index, the lower the better.
    The structural index represents the portion of the mass used by 
    the structure of the tank.
    Solid propellant can only be used for the first stage.
    Liquid Hydrogen cannot be used for the first stage.

    Args:
        prop_type (str): Name of the propellant used. 
        - LH2 is liquid hydrogen. 
        - RP1 is rocket grade kerosene. 
        - SOLID is self explainatory.
        stage_number (int): Number of the stage for the propellant used.
        (1 is the first stage, at the bottom of the rocket).

    Raises:
        ValueError: If the provided propellant is not in ["RP1", "LH2", "SOLID"] or if the given propellant cannot be used for the stage.

    Returns:
        int: ISP of the propellant
        float: structural index of the tank containing the propellant.
    """
    if prop_type.upper() == "RP1":
        Isp = 287 if stage_number == 1 else 330
        struc_index = 0.15
    elif prop_type.upper() == "LH2" and stage_number != 1:
        Isp = 440
        struc_index = 0.22
    elif prop_type.upper() == "SOLID" and stage_number == 1:
        Isp = 260
        struc_index = 0.10
    else:
        raise ValueError
    return Isp, struc_index


def get_propellant_specs(list_of_propellants):
    """Utility function that returns all the ISPs and Structural indices of each stage
    in a list ordered by stage.

    Args:
        list_of_propellants (List[str]): List of propellants used, 
        stage by stage, in order from stage 1 to n (bottom to top)

    Returns:
        List[int]: ISPs of each stage, ordered bottom stage (1) to top stage (n).
        List[float]: Stuctural indices of each stage, ordered bottom stage (1) to top stage (n).
    """
    ISP = []
    structural_index = []
    for stage, prop_type in enumerate(list_of_propellants, start=1):
        i, k = Propellant_spec(prop_type, stage)
        ISP.append(i)
        structural_index.append(k)
    return ISP, structural_index


def Stage_Optimisation(stages, required_dVp: float, payload_mass: float, starting_b_value: float = 1.0001, min_stage1_mass: float = 500, min_stageN_mass: float = 200):
    """Automaticaly finds the most optimized rocket configuration using the given stage propellant list. A list of n elements will result in a rocket with n stages. Each stage uses the propellant specified. Choices are RP1, LH2 or Solid.
    The function will try to build a rocket with a propulsive Delta V >= required_dVp. 
    Payload mass must be specified because it is important in the sizing of the rocket.

    Args:
        stages (List[str]): List of propellants used, stage by stage, in order from stage 1 to n (bottom to top).
        required_dVp (float): Velocity required by the mission for injection.
        payload_mass (float): Mass of the payload/satellite from the mission data.
        starting_b_value (float, optional): value of the factor b at the start of the algorithm. Defaults to 1.

    Returns:
        List[int]: ISPs of each stage, in a list ordered by stage 
        List[float]: Delta V of each stage, in a list ordered by stage 
        List[float]: incremental mass of each stage, in a list ordered by stage 
        List[float]: fuel mass of each stage, in a list ordered by stage 
        List[float]: structural mass of each stage, in a list ordered by stage 
    """

    n = len(stages)

    ISP, k = get_propellant_specs(stages)

    a = [0] * n
    b = [0] * n
    dV = [0] * n
    M = [0] * n
    M.append(payload_mass)
    m_e = [0] * n
    m_s = [0] * n

    Omega = [0] * n
    for i in range(n - 1, -1, -1):
        Omega[i] = k[i] / (1 + k[i])

    # ------------- Lagrange Multiplier Method ---------------

    b[n - 1] = starting_b_value  # arbitrary
    while True:
        dV[n - 1] = lib.const.EARTH_GRAV_SEA_LVL * \
            ISP[n - 1] * np.log(b[n - 1])
        for j in range(n - 2, -1, -1):
            b[j] = 1 / Omega[j] * (1 - ISP[j + 1] / ISP[j] *
                                   (1 - Omega[j + 1] * b[j + 1]))
            dV[j] = lib.const.EARTH_GRAV_SEA_LVL * ISP[j] * np.log(b[j])

        if sum(dV) >= required_dVp:
            for i in range(n - 1, -1, -1):
                a[i] = (1 + k[i]) / b[i] - k[i]
                M[i] = M[i + 1] / a[i]
                m_e[i] = M[i] * (1 - a[i]) / (1 + k[i])
                m_s[i] = k[i] * m_e[i]

            # Stage 1 > 500 kg
            # Stage N > 200 kg
            # Mass Stage i > total mass stages above
            if m_s[0] < min_stage1_mass or any(elem < min_stageN_mass for elem in m_s[1:]) or any(
                (m_s[i] + m_e[i]) <
                (sum(m_e[i + 1:]) + sum(m_s[i + 1:]) + M[-1])
                    for i in range(n - 2, -1, -1)):
                # Conditions are not fulfilled
                b[n - 1] += 0.0001
                continue
            # Conditions are fulfilled
            break
        b[n - 1] += 0.0001
    return ISP, dV, M, m_e, m_s


def create_combinations(min_number_stages: int = 2, max_number_stages: int = 3, available_propellants=["Solid", "RP1", "LH2"]):
    """Generates all the possible and valid propellant configurations.

    Args:
        min_number_stages (int, optional): Minimum number of stages for the rocket. Defaults to 2.
        max_number_stages (int, optional): Maximum number of stages for the rocket. Defaults to 3.
        available_propellants (list, optional): List of all available propellants (should be ordered by possible stage use, lower to upper). Defaults to ["Solid", "RP1", "LH2"].

    Returns:
        List[List[str]]: List of all the possible combinations
    """
    from itertools import combinations_with_replacement
    combinations = []
    for k in range(min_number_stages, max_number_stages + 1):
        combs = combinations_with_replacement(available_propellants, r=k)
        for comb in combs:
            if check_propellant_combination(comb):
                combinations.append(list(comb))
    return combinations


def check_propellant_combination(combination):
    """Verifies that Solid propellant can only be used as first stage and that LH2 cannot be used as first stage

    Args:
        combination (List[str]): a combination of propellants ordered by stage

    Returns:
        bool: is the combination possible ?
    """
    if combination[0].upper() == "LH2":
        return False
    if "Solid" in combination[1:]:
        return False
    return True


def best_rocket(required_dVp: float, payload_mass: float, min_number_stages: int, max_number_stages: int, available_propellants, starting_b_value, min_stage1_mass, min_stageN_mass):

    stages_combinations = create_combinations(
        min_number_stages, max_number_stages, available_propellants)

    best_mass = float('inf')  # initialization
    for stages in stages_combinations:
        ISP, dV, M, m_e, m_s = Stage_Optimisation(
            stages, required_dVp, payload_mass, starting_b_value, min_stage1_mass, min_stageN_mass)

        if M[0] < best_mass:
            best_mass = M[0]
            best_ISP, best_dV, best_M, best_m_e, best_m_s = ISP, dV, M, m_e, m_s
            best_propellant_configuration = stages

    return best_propellant_configuration, best_ISP, best_dV, best_M, best_m_e, best_m_s


# -------------------- Main ----------------------

if __name__ == "__main__":

    # <-- input the mission scenario
    azimut, Vf, Vi, Vl, dVp, m_cu = Injection_Requirements("mission3")

    # <-- input various parameters to automatically find the lightest rocket possible
    stages, ISP, dV, M, m_e, m_s = best_rocket(dVp, m_cu, min_number_stages=2, max_number_stages=4, available_propellants=[
                                               "Solid", "RP1", "LH2"], starting_b_value=1.0001, min_stage1_mass=500, min_stageN_mass=200)

    # ----------------- Prints -------------------
    print("\n-------------- Mission parameters --------------")
    print("azimuth ", round(azimut, 2))
    print("V required", round(Vf, 2), " m/s.")
    print("V init ", round(Vi, 2), " m/s.")
    print("Losses ", round(Vl, 2), " m/s.")
    print("\nDelta V required ", round(dVp, 2), " m/s.")
    print("\n-------------- Rocket parameters --------------")
    print(f"\nTotal propulsive Delta V = {sum(dV)}")
    print("\nTotal mass ", M[0])
    print('\nPropellants used ', stages)

    for i in range(len(stages)):
        print("\n------------------------------------------------")
        print(f"---------------     Stage {i+1}    -----------------\n")
        print(f"Delta V stage {i+1} = {dV[i]}")
        print(f"\nISP stage {i+1} = {ISP[i]}")
        print(f"\nMass of Stage {i+1} = {m_s[i] + m_e[i]}")
        print(f"Propellant mass stage {i+1} = {m_e[i]}")
        print(f"Structural mass stage {i+1} = {m_s[i]}")
