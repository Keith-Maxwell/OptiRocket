# School project

This is the original subject of our school project.

## Context

At IPSA Rocket Company (IRC), we are working on launcher conception and are involved in the development of launchers for space agencies. Our work is to design a launcher for one of the specific mission profiles given. The design consists in determining the optimal staging of the launcher to make the mission a success :

- the number of stages
- the appropriate propellant type
- the distribution of masses in each stage
- the azimut

## Missions

1. [Cargo to ISS](optirocket/missions/ISScargo.json) : Roscosmos wants to deliver cargo to the international space station
1. [Military satellite](optirocket/missions/POLARsat.json) : a Military agency need a satellite in a polar and circular orbit
1. [GEO satellite](optirocket/missions/GEOsat.json) : ESA requires a GEO satellite. Put the satellite on a geostationary transfer orbit.
1. [SSO satellite](optirocket/missions/SSOsat.json) : NASA wants to send a satellite on a Sun-Synchronous orbit at a constant altitude.

## Goals

This project allows to determine the injection requirements, the optimal staging of the rocket using the Lagrange Multiplier method, and the final orbital elements.

## Authors

- Max Perraudin
- Marie Dupont
- Paul Sole
