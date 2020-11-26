import numpy as np
import importlib
import library.orbit_lib as lib


# ------------ Definitions ---------------


def Injection_Requirements(mission: str = "mission5"):
    """
    Returns the Azimuth, Required velocity, initial velocity, losses, Propulsive Delta V and payload mass

    Takes the name of the mission file as input (without the extension)
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
    """
    Returns the ISP and Structural index of a stage, given its propellant type and stage number

    Input is the prop type and the stage number
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


def Propellant(list_of_propellants):
    """
    Returns 2 lists : ISP and structural index, ordered by stage

    Input is a list of propellant types ordered by stage starting from bottom to top
    """
    ISP = []
    structural_index = []
    for stage, prop_type in enumerate(list_of_propellants, start=1):
        i, k = Propellant_spec(prop_type, stage)
        ISP.append(i)
        structural_index.append(k)
    return ISP, structural_index


def Stage_Optimisation(stages, required_dVp: float, M_u: float, starting_b_value: float = 3):
    """
    Returns the ISP, delta V, Stage mass, Mass of fuel and structural mass of every stage. The returned elements are lists.

    Takes as an input a list of propellant types ordered by stage starting from bottom to top, the required Delta V and the payload mass.
    """
    n = len(stages)

    ISP, k = Propellant(stages)

    a = [0] * n
    b = [0] * n
    dV = [0] * n
    M = [0] * n
    M.append(M_u)
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

            if m_s[0] < 500 or any(elem < 200 for elem in m_s[1:]) or any(
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


# -------------------- Main ----------------------


if __name__ == "__main__":
    # <-- input the mission scenario
    azimut, Vf, Vi, Vl, dVp, m_cu = Injection_Requirements("mission3")

    # <-- input the stages propellants, from bottom to top.
    stages = ["solid", "LH2"]

    ISP, dV, M, m_e, m_s = Stage_Optimisation(stages, dVp, m_cu)

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

    for i in range(len(stages)):
        print("\n------------------------------------------------")
        print(f"---------------     Stage {i+1}    -----------------\n")
        print(f"Delta V stage {i+1} = {dV[i]}")
        print(f"\nISP stage {i+1} = {ISP[i]}")
        print(f"\nMass of Stage {i+1} = {m_s[i] + m_e[i]}")
        print(f"Propellant mass stage {i+1} = {m_e[i]}")
        print(f"Structural mass stage {i+1} = {m_s[i]}")
