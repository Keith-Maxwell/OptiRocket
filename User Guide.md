# User Guide

## Initialize the `OptiRocket` class

```python
rocket = OptiRocket()
```

## Specify the mission

there are two ways to define the mission. Import the mission file or manually set the parameters.

1. Import from mission file

   I have a mission file located in `missions/` folder. the file is a python file so it ends with `.py` but the extension is not included in the call.

   ```py
   rocket.mission(filename="mission.mission1")
   ```

1. Manually specify the parameters

   ```py
   rocket.mission(client_name="Roscosmos",
               altitude_perigee= 410,
               altitude_apogee= 410,
               inclination= 51.6,
               mass_payload= 32000,
               launchpad= "Baikonur",
               launchpad_latitude= 45.6)
   ```

   The attributes `client_name` and `launchpad` are optional, but all the others are mandatory.

## Compute the requirements

The mission defines the altitude and inclination of the targeted orbit. We can determine the required velocity, the losses due to atmospheric drag, the azimuth of the launch, etc...

```py
rocket.compute_requirements()
```

There is no output to this command yet, but values can be accessed by calling them, for example `rocket.azimuth`

## Available propellants

There are 3 predefined propellants :

| Name                 | Code  | Possible stages | ISP (vacuum) | mean ISP | Structural index |
| -------------------- | :---: | :-------------: | :----------: | :------: | :--------------: |
| Refined petroleum    |  RP1  |  1, 2, 3, ...   |     330      |   287    |       0.15       |
| Liquid Hydrogen      |  LH2  |    2, 3, ...    |     440      |    -     |       0.22       |
| Solid Rocket Booster | SOLID |        1        |     300      |   260    |       0.1        |

It is possible to define new propellants. This can be done using the method :

```py
rocket.add_available_propellant(name="Hydrazine",
                                possible_stages=[2, 3],
                                isp=290,
                                mean_isp=240,
                                structural_index=0.15)
```

Using the same name as an already existing propellant will overwrite it.

## Setting the limits on the mass

### Minimum and maximum structural mass

### Maximum total mass
