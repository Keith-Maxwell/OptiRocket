import numpy as np

# Test pour mission 2:
# Client: Military
# Injection Zp = 340 km
# Za = 340km
# inc = 90 deg
# Mass cargo = 290 kg
# Launch pad: Vanderberg (34.7)

# Azimuth determination:

i=90
phi=34.7

a = np.arcsin(np.cos(i)/np.cos(phi))
print("L'azimuth du lancement est égal à ",np.degrees(a)," degrés.")

# Propulsive dV determination:

mu = 3.986005e5  #(km3/s2) Earth GM
Re = 6778.137    #(km) Earth Radius
zp = 340         #(km) injection altitude
wE = 7.2921e-5     #(km/s) truc avec période sidérale

Vf= np.sqrt(mu/(Re+zp))*10**3 #(m/s) Circular orbit velocity
print("La vitesse de satélisation est égale à ",Vf," m/s.")  

Vi= wE * Re * np.cos(phi) * np.sin(a)*10**3 #(m/s)
print("Je sais pas quoi est égal à ",Vi," m/s.")

Vl =  (2.452e-3) * zp**2 + 1.051 * zp + 1387.50 # (m/s) losses
print("Les pertes sont estimées à ",Vl," m/s.")

dVp= Vf - Vi +Vl #(m/s) Propulsive dV
print("Le DeltaV nécessaires pour s'orbiter est de ",dVp," m/s.")

