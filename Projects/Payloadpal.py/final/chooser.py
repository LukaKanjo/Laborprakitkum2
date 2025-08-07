from classes import payload, rocket, planet, location
# Planet
def choose_planet(options: dict[str, planet]) -> planet:
  print("Choose your planet: ")
  for key, obj in options.items():
    print(f" {key}: {obj.name}")
  planet_choice = input("Choose your planet [1]: ").strip()
  selected = options.get(planet_choice, options["1"])
  stats = f"""You have selected the {selected.name}!
Key Stats:

    - Mass = 5.97 * 10^24 [kg]
    - Radius = 6371 [km]
    - Accleration due to gravity = 9.81 [m/s]
    - Orbit height (LEO) = 400 [km]

"""
  print(stats)
  return selected

# Payload

def choose_payload(options: dict[str, payload]) -> payload: 
  # Arg options muss dictionary sein und dessen Key = str, "-> payload" ist der rückgabetyp
  print("\nChoose your payload: ")
  for key, obj in options.items():
     print(f" {key}: {obj.payload_type} ({obj.mass_kg} kg)")
  payload_choice = input("Your choice [1-4]: ").strip()
  
  return options.get(payload_choice, options["1"])  
# options.get(choice) sucht im Dict nach Key, options[choice] grabs the choice, option 1 is our backup


# Choose Rocket
def choose_rocket(options: dict[str, rocket]) -> rocket:
  print("Choose your rocket: ")
  for key, obj in options.items():
    print(f" {key}: {obj.model} (Current payload: {obj.payload.mass_kg} kg)")
  rocket_choice = input("Your choice [1]: ").strip()
  selected = options.get(rocket_choice, options["1"])
  stats = f"""\nYou have selected the {selected.model} rocket!
Key Stats:

    \n- Total height: {selected.height} m
    - Diameter: {selected.diameter} m
    - Empty mass: {selected.empty_mass:.0f} kg
    - Fuel mass: {selected.fuel_mass:.0f} kg
    - Specific impulse (sea level): {selected.isp_sea_lvl} s
    - Specific impulse (vacuum): {selected.isp_vacuum} s
    - Maximum payload to low Earth orbit: {selected.payload.mass_kg:.0f} kg
    - Number of stages: 2
    - Thrust: {selected.thrust} N

"""
  print(stats)
  return selected

def choose_location(options: dict[str, rocket]) -> location:
  print("Choose your location: ")
  for key, obj in options.items():
    print(f"{key}: {obj.name}")
  location_choice = input("Your choice: ")
  selected = options.get(location_choice, options["1"])
  return selected

