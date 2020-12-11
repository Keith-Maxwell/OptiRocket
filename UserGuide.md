# User Guide

## Initialize the `OptiRocket` class

```python
rocket = OptiRocket()
```

## Specify the mission

there are two ways to define the mission. Import the mission file or manually set the parameters.

### Import from mission file

If you have a mission file, you can import it directly. A mission file is a `.json` file containing all the info needed. ([Template](optirocket/missions/GEOsat.json)).

To import the mission file, simply call :

```py
rocket.mission(filename="path/to/file.json")
```

#### Default missions

|                                 | ISScargo.json | POLARsat.json | GEOsat.json |  SSOsat.json   | LEOsat.json |
| ------------------------------- | :-----------: | :-----------: | :---------: | :------------: | :---------: |
| Client                          |   Roscosmos   |   Military    |     ESA     |      NASA      |     ESA     |
| Injection/Altitude perigee (km) |      410      |      340      |     200     |      567       |     300     |
| Altitude apogee (km)            |      410      |      340      |    35786    |      567       |     300     |
| Inclination (degrees)           |     51.6      |      90       |     5.2     |      97.6      |     49      |
| Mass of the payload (kg)        |     32000     |      290      |    3800     |      1150      |     300     |
| Launchpad                       |   Baikonur    |  Vandenberg   |   Kourou    | Cape Canaveral |   Kourou    |
| Launchpad latitude (degrees)    |     45.6      |     34.7      |     5.2     |      28.5      |     5.2     |

### Manually specify the parameters

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

To prepare the optimization process, use the method :

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

Using the same name as an already existing propellant will overwrite it. The list of available propellants is stored in the variable `available_propellants`

## Setting the limits on the mass

Maybe your rocket must be constrained regarding its mass. In this case, you can manually set the min and max values. These values will be respected by the optimization algorithm.

By default, there are no limits.

### Minimum and maximum structural mass

If you have constraints on the rocket structural mass, you can input them by using the method `set_masses_limits()`. This is optional. The arguments to pass the method are the `stage`, the `min` and the `max`structural mass. This way, each stage can have different limits.

For example, if your stage 1 must be over 2000 kg and under 10000 kg, you can call the method like this :

```py
rocket.set_masses_limits(stage=1, min=2000, max=10000)
```

### Maximum total mass

The launchpad may require the rocket to be under a certain mass. If this is the case, you can define the maximal total mass of the rocket (fully fueled) using the method `set_max_total_mass()`.

For example, if your launchpad limits to 1 200 000 kg :

```py
rocket.set_max_total_mass(max_total_mass=1200000)
```

## Stage optimization

### Optimizing for a specific propellant combination

In the case you know which propellant and stages you want to use, you can optimize the dimensions of your rocket by simply giving the list of the propellants, in order of use, from first stage to last stage to the method `stage_optimization()`.

For example, if your desired rocket has a Solid first stage, a RP1 second stage, and a LH2 third stage, simply pass the list `["SOLID", "RP1", "LH2"]`

```py
rocket.stage_optimization(["SOLID", "RP1", "LH2"])
```
