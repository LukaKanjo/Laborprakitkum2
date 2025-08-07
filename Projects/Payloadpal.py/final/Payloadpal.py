import math as m
import matplotlib.pyplot as plt
import pandas as pd
import scipy 
import time

# Instanzen erstellen:
from classes import payload, rocket, planet, location
# Chooser breits integrieren
from chooser import choose_location, choose_payload, choose_rocket, choose_planet


def main():
# Planets
    earth = planet(
        name = "Earth", 
        mass = 5.97e24, 
        radius = 6.371e6, 
        G_const = 6.7e-11, 
        g_const = 9.81,
        height_orbit = 400000,
        rotation_period = 86400
        )
    planet_options = {
        "1": earth
    }

    chosen_planet = choose_planet(planet_options)
    print(f"\nChosen planet: {chosen_planet.name}")
    print(f"\nOrbit velocity = {chosen_planet.v_orbit}")

# Payload
    hawk_link_v2 = payload("unmanned with a Hawk Link V2 Satellite", mass_kg = 1200)  # Off-brand Starlink v2
    crew1_payload = payload("manned", crew_number = 1)
    crew4_payload = payload("manned", crew_number = 4)
    crew6_payload = payload("manned", crew_number = 6)
    # Dict kreieren für Chooser
    payload_options = {
    "1": hawk_link_v2,
    "2": crew1_payload,
    "3": crew4_payload,
    "4": crew6_payload
    }

    chosen_payload = choose_payload(payload_options)
    print(f"\nChosen payload: {chosen_payload.payload_type} ({chosen_payload.mass_kg} kg)\n")

# Stages: Rocket Systems
    rocket_syst = {}

# Hawk 9 V1.1 - 2 Stages (based on Falcon 9)

    stage2_hawk9 = rocket(
        model="Hawk 9 Stage 2",
        height=15,
        diameter=3.7,
        empty_mass=3900,
        isp_sea_lvl = 340,  # No specific Impulse at sea lvl for stage 2 => isp_avg = isp_vacuum = 348 s
        isp_vacuum=340,
        payload = chosen_payload,
        fuel_mass=92670,
        thrust=801_000,
        C_d=0.3,
    )

    stage1_hawk9 = rocket(
    model="Hawk 9 Stage 1",
    height=45,
    diameter=3.7,
    empty_mass=25_600,
    isp_sea_lvl=282,
    isp_vacuum=311,
    payload=payload("stage2", mass_kg=stage2_hawk9.start_mass),
    fuel_mass=395_000,   # Research Gate mass ind
    thrust=5_900_000,
    C_d=0.3
)

    rocket_syst["1"] = [stage1_hawk9, stage2_hawk9] #System für Hawk 9

    # Für weitere Raketen: rocket_syst["2"] = [stage1_other, stage2_other]

# Rocket
    '''hawk_9 = rocket(
        model = "Hawk 9 Stage 2", 
        height = 70,
        diameter = 3.7, # [m]
        empty_mass = 0.1 * 5.49e5, # [kg]
        isp_sea_lvl = 282,
        isp_vacuum = 348, # [s]
        payload = chosen_payload, 
        fuel_mass = 0.85 * 5.49e5,
        thrust = 7.6e6, # [N]
        C_d = 0.3
    )'''

    
    
    rocket_options = {
        "1": stage1_hawk9
    }
    chosen_rocket   = choose_rocket(rocket_options)
    print(f"\nChosen rocket: {chosen_rocket.model}\n")
    chosen_stages = rocket_syst["1"]
# Locations
    vienna = location("Sternwarte", 48.2)
    luxembourg = location("Sandweiler, Luxembourg", 49.6)
    guyana = location("French Guyana Space Centre", 5.2)
    us = location("SpaceX Launch Pad in Brownsville, Texas", 26.0)    
    location_options = {
        "1": vienna,
        "2": luxembourg,
        "3": guyana,
        "4": us
    }

# Interaktive auswahl
    chosen_location = choose_location(location_options)
    print(f"\nChosen location: {chosen_location.name}\n")
    rot_v = chosen_location.rot_bonus(chosen_planet)
    print(f"\nRotational velocity boost at {chosen_location.name}: {rot_v:.1f} m/s")

# Simulation und Daten
    flight_stage1 = chosen_stages[0].simulate_flight(chosen_planet, chosen_location, dt = 0.5, v0 = 0, thrust_ramp_time = 5.0,
    rot_boost_ramp_time = 150.0)   # v0 = v_rot
    last = flight_stage1[-1]
    m_offset = last['m'] - stage2_hawk9.start_mass
    flight_stage2 = stage2_hawk9.simulate_flight(
    chosen_planet,
    chosen_location,
    dt=0.5,
    v0=last["v"],
    h0=last["h"],
    t0=last["t"],
    m_offset = m_offset,
    thrust_ramp_time = 5.0,
    rot_boost_ramp_time = 60.0
    )

    last1 = flight_stage1[-1]   # Letzter Datenpunkt für Stage 1
    
    # Debugging
    """print("--- Stage 1 Values @ start ---")
    print(f"Startmasse         : {stage1_hawk9.start_mass:.0f} kg")
    print(f"Thrust             : {stage1_hawk9.thrust:.0f} N")
    print(f"Isp (avg)          : {stage1_hawk9.isp:.1f} s")

    print(f"\n Handover at Stage 2:")
    print(f"  t = {last['t']:.1f} s")
    print(f"  v = {last['v']:.1f} m/s")
    print(f"  h = {last['h']:.1f} m")
    print(f"  m = {last['m']:.1f} kg")
    for point in flight_stage2:
        point["t"] += last1["t"]
        point["v"] += last1["v"]
        point["h"] += last1["h"]"""

    df_earth = pd.DataFrame(flight_stage1 + flight_stage2)



    # Statistics
    t_burn = df_earth["t"].max()
    v_max = df_earth["v"].max()
    h_max = df_earth["h"].max()

    print(df_earth.columns.tolist())

    # Output
    print("\n--- Flightsimulation Results ---")
    print(f"Burn time       : {t_burn:.1f} s")
    print(f"Maximum velocity: {v_max:.1f} m/s")
    print(f"Maximum altitude: {h_max:.1f} m\n")


    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=False)

    # 1) v(t)
    axes[0, 0].plot(df_earth["t"], df_earth["v"], color = "orangered")
    axes[0, 0].set_title("Velocity over time")
    axes[0, 0].set_ylabel("v [m/s]")
    axes[0, 0].set_xlabel("t [s]")
    axes[0, 0].set_ylim(bottom=0)

    # 2) h(t)
    axes[0, 1].plot(df_earth["t"], df_earth["h"] * 1e-3, color = "deepskyblue")
    axes[0, 1].set_title("Height over time")
    axes[0, 1].set_ylabel("h [km]")
    axes[0, 1].set_xlabel("t [s]")
    axes[0, 1].set_ylim(bottom=0)

    # 3) a(t)
    axes[0, 2].plot(df_earth["t"], df_earth["a"], color = "gold")
    axes[0, 2].set_title("Acceleration over time")
    axes[0, 2].set_ylabel("a [m/s²]")
    axes[0, 2].set_xlabel("t [s]")
    axes[0, 2].set_ylim(bottom=0)

    # 4) m(t)
    axes[1, 0].plot(df_earth["t"], df_earth["m"] * 1e-3, color = "fuchsia")
    axes[1, 0].set_title("Mass over time")
    axes[1, 0].set_ylabel("m [T]")
    axes[1, 0].set_xlabel("t [s]")
    axes[1, 0].set_ylim(bottom=0)

    # 5) Drag force
    axes[1, 1].plot(df_earth["t"], df_earth["F_d"] * 1e-3, color = "forestgreen")
    axes[1, 1].set_title("Drag over time")
    axes[1, 1].set_ylabel("F [kN]")
    axes[1, 1].set_xlabel("t [s]")
    axes[1, 1].set_ylim(bottom=0)

    # 6) Rotational boost
    if "rot_boost" in df_earth.columns:
        axes[1, 2].plot(df_earth["t"], df_earth["rot_boost"], color = "darkviolet")
        axes[1, 2].set_title("Rotational boost over time")
        axes[1, 2].set_ylabel("boost [m/s]")
        axes[1, 2].set_xlabel("t [s]")
        axes[1, 2].set_ylim(bottom=0)
    else:
        axes[1, 2].axis("off")

    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    main()

