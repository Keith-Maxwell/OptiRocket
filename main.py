import numpy as np
import importlib
import mission2 as data


mu = 3.986005e5  #(km3/s2) Earth GM
Re = 6378.137  #(km) Earth Radius
wE = 6.300387486749 / 86164  #(rad/s) Earth rotation speed (calculated from période sidérale)
g0 = 9.80665  #Earth gravitation at sea level (m^2/s)


def Requirements(mission="mission2"):
    data = importlib.import_module(mission)
    # Calculate the azimuth (in radians)
    azi = np.arcsin(
        np.cos(np.radians(data.inc)) / np.cos(
            np.radians(data.launchpad_latitude)))
    # Circular orbit velocity (m/s)
    V_final = np.sqrt(mu / ((2 * Re + data.Z_p + data.Z_a) / 2)) * 10**3
    # Initial velocity due to Earth Rotation (m/s)
    V_init = wE * Re * 10**3 * np.cos(np.radians(
        data.launchpad_latitude)) * np.sin(azi)
    # Delta V losses due to atmospheric drag and more (m/s)
    V_losses = (2.452e-3) * data.Z_p**2 + 1.051 * data.Z_p + 1387.50
    # Propulsive dV required to get to the desired orbit (m/s)
    dVp = V_final - V_init + V_losses
    return azi, V_final, V_init, V_losses, dVp


def Propellant_spec(prop_type, stage_number):
    if prop_type == "RP1":
        if stage_number == 1:
            Isp = 287
        else:
            Isp = 330
        struc_index = 0.15

    elif prop_type == "LH2":
        Isp = 440
        struc_index = 0.22

    else: # solid
        if stage_number == 1:
            Isp = 260
        else:
            Isp = 300
        struc_index = 0.10

    return Isp, struc_index




azimut, Vf, Vi, Vl, dVp = Requirements()
# Print :
print("azimuth ", round(np.degrees(azimut), 2))
print("V required", round(Vf, 2), " m/s.")
print("V init ", round(Vi, 2), " m/s.")
print("Losses ", round(Vl, 2), " m/s.")
print("Delta V required ", round(dVp, 2), " m/s.")


ISP1, k1 = Propellant_spec("Solid", 1)
ISP2, k2 = Propellant_spec("LH2", 2)
Omega2 = k2 / (1+k2)
Omega1 = k1 / (1+k1)

b2 = 3 # arbitrary
while True:
    b1 = 1/Omega1 * (1 - ISP2/ISP1 * (1 - Omega2 * b2))
    dV1 = g0 * ISP1 * np.log(b1)
    dV2 = g0 * ISP2 * np.log(b2)
    dV = dV1 + dV2
    if dV > dVp:
        M_u = data.m_payload
        a1 = (1+k1) / b1 - k1
        a2 = (1+k2) / b2 - k2
        M2 = M_u / a2
        M1 = M2/ a1
        m_e1 = M1 * (1-a1) / (1+k1)
        m_e2 = M2 * (1-a2) / (1+k2)
        m_s1 = k1 * m_e1
        m_s2 = k2 * m_e2
        if m_s1 < 500 or m_s2 < 200:
            b2 += 0.001
            continue
        break
    b2 += 0.0001

print("Delta V : ", dV)
print ("\nIPS1", ISP1, "k1", k1)
print ("IPS2", ISP2, "k2", k2)
print("\nStage 1 ", m_s1 + m_e1, "\nStage 2 ", m_s2 + m_e2)
print("Total mass ", M1)
print("propellant mass stage 1 ", m_e1)
print("propellant mass stage 2 ", m_e2)
print("Structural mass stage 1 ", m_s1)
print("Structural mass stage 2 ", m_s2)
print("DeltaV1= ",dV1)
print("DeltaV2= ",dV2)



