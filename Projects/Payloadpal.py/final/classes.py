import math as m
import matplotlib as plt
import pandas as pd
import scipy 

class payload:
    """
    Modelliert eine Nutzlast für die Rakete.
    Unterstützt bemannte und unbemannte Missionen.
    """
    MASS_PER_CREW = 70  # kg, typischer Wert pro Crewmitglied

    def __init__(self, payload_type, crew_number=0, mass_kg=None, crew_name=None):
        """
        Initialisiert eine Payload-Instanz.
        :param payload_type: Art der Nutzlast ('manned', 'unmanned', 'satellite')
        :param crew_number: Anzahl Crewmitglieder (nur relevant für 'manned')
        :param mass_kg: Masse der Nutzlast (falls None, wird für 'manned' berechnet)
        :param crew_name: Name(n) der Crew (optional)
        """
        self.payload_type = payload_type
        self.crew_number = crew_number if payload_type == "manned" else 0
        self.crew_name = crew_name

        if mass_kg is None:
            if payload_type == "manned":
                self.mass_kg = self.crew_number * self.MASS_PER_CREW
            else:
                self.mass_kg = 0
        else:
            self.mass_kg = mass_kg

    @property
    def is_manned(self):
        """Gibt True zurück, wenn die Payload bemannt ist."""
        return self.payload_type.lower() == "manned"

    @property
    def is_unmanned(self):
        """Gibt True zurück, wenn die Payload unbemannt ist."""
        return not self.is_manned


class rocket:
    """
    Modelliert eine Rakete.
    """
    def __init__(self, model, height, diameter, empty_mass, isp_sea_lvl, isp_vacuum, payload, fuel_mass, thrust, C_d):
        """
        Initialisiert eine Raketen-Instanz.
        :param model: Name des Raketentyps
        :param height: Gesamthöhe (m)
        :param diameter: Durchmesser (m)
        :param empty_mass: Leermasse (kg)
        :param isp_sea_lvl: spezifischer Impuls auf der Erde(s)
        :param isp_vacuum: spezifischer Impuls im Vakuum(s)
        :param payload: Payload-Objekt
        :param fuel_mass: Treibstoffmasse (kg)
        """
        self.model = model
        self.height = height
        self.diameter = diameter
        self.empty_mass = empty_mass
        self.isp_sea_lvl = isp_sea_lvl
        self.isp_vacuum = isp_vacuum
        self.payload = payload
        self.fuel_mass = fuel_mass
        self.isp = self.isp_avg
        self.thrust = thrust




    @property
    def start_mass(self):
        """Berechnet die Gesamt-Startmasse der Rakete (inkl. Treibstoff und Payload)."""
        return self.empty_mass + self.fuel_mass + (self.payload.mass_kg if self.payload else 0)

    @property
    def mass_ratio(self):
        """Berechnet das Massenverhältnis (Startmasse / Leermasse+Payload)."""
        return self.start_mass / (self.empty_mass + (self.payload.mass_kg if self.payload else 0))

    def delta_v(self, g0=9.81):
        """
        Berechnet das maximal erreichbare Delta-v (m/s) nach Tsiolkovsky.
        :param g0: Standard-Gravitationskonstante (m/s²), default=9.81
        :return: Delta-v in m/s
        """
        if self.fuel_mass > 0 and self.start_mass > (self.empty_mass + self.payload.mass_kg):
            return self.isp * g0 * m.log(self.start_mass / (self.empty_mass + self.payload.mass_kg))
        else:
            return 0
        
    @property
    def isp_avg(self):
        """
        Berechnet einen gewichteten durchschnittlichen spezifischen Impuls 
        (empfohlen: 80% Sea Level, 20% Vakuum).
        """
        return 0.8 * self.isp_sea_lvl + 0.2 * self.isp_vacuum
    
    def simulate_flight(self, planet, location, dt: float = 0.5, v0: float = 0.0, h0: float =  0.0, t0: float = 0.0, m_offset: float = 0.0, thrust_ramp_time: float = 5.0, rot_boost_ramp_time: float = 60.0) -> list[dict]:
        """
        Numerische Integration von m(t), a(t), v(t), h(t).
        planet: Objekt mit g_const
        dt: Zeitschritt in s
        """
        # Rot Boost dependant of chosen_location
        rot_v = location.rot_bonus(planet)

        # Klassenerweiterung für Raketengleichung Plot    

        # Ausströmgeschwindigkeit ve definieren
        ve = self.isp * planet.g_const
        
        # Massendurchsatz m dot -> Menge an ausgestoßener Masse pro Zeit
        mdot = self.thrust / ve # [kg * (m/s^2)] / [m/s] => [kg/s]

        # Drag preparation
        self.C_d = 0.3  # Drag coefficient, estimated for Falcon 9
        self.A = m.pi * (self.diameter / 2)**2

        self.burn_time = self.fuel_mass / mdot

        # Ausströmgeschwindigkeit und mdot einmal berechnen
        ve   = self.isp * planet.g_const
        mdot = self.thrust / ve

        # Sets all parameters to 0, before launch
        t = t0
        v = v0
        h = h0
        data = []

        while t <= self.burn_time:
            # Progressive thrust
            thrust_factor = min(t / thrust_ramp_time, 1.0)
            # t / thrust_ramp_time indicates how far in the ramp and 1.0 eliminates further rise
            current_thrust = thrust_factor * self.thrust

            # boost_ramp
            rot_boost_factor = min(t / rot_boost_ramp_time, 1.0)
            current_rot_boost = rot_boost_factor * rot_v


            fuel_remaining = max(self.fuel_mass - mdot * t, 0)
            
            m_t = self.empty_mass + self.payload.mass_kg + fuel_remaining
            
            # Abortion, if Mass becomes irrealistic
            if m_t < 10 or not m.isfinite(m_t):
                print(f"Simulation aborted: Invalid mass m = {m_t: .2f} kg at t  = {t: .1f} s")
                break


            # Drag
            if h > 100_000:
                rho = 0
            else:
                rho = 1.225 * m.exp(-h / 8500)  # kg/m^3
            
                    # Pitchwinkel über Zeit abnehmen

            # Drag calculation
            F_d = 0.5 * rho * self.C_d * self.A * v**2  # Drag formula
            

            
            m_t = self.empty_mass + self.payload.mass_kg + max(self.fuel_mass - mdot*t, 0)
            # Test a
            a   = ((current_thrust - F_d) / m_t) - planet.g_const
            if a <= 0:
                a = 0
            # 1) Thrust and gravitational acceleration
            v  += a * dt
            # 2) Rotational boost
            v += current_rot_boost * (dt / rot_boost_ramp_time)

            h = max(h + v * dt, 0)  # Begrenzung, dass Rakete nicht unter Boden geht

            if not m.isfinite(v) or abs(v) > 1e5:   # 1e5 = boundary, rockets shouldn't be able to reach 1e5 m/s
                print(f"\nSimulation aborted: Invalid velocity v = {v: .2f} m/s at t = {t: .1f}s")
                break

            data.append({"t": t, "v": v, "h": h, "a": a,"m": m_t + m_offset, "F_d": F_d, "rot_boost": current_rot_boost})

            if v >= planet.v_orbit or h >= planet.height_orbit:
                print(f"\nCongratulations Captain! LEO was reached at t = {t: .1f} s, v = {v:.1f} m/s, m = {m_t: .0f} kg")
                break

            m_offset = 0    # For stage 2

            t  += dt

        return data


class planet:
    """
    Modelliert einen Planeten.
    """
    def __init__(self, name, mass, radius, rotation_period, G_const, g_const, height_orbit):
        """
        Initialisiert einen Planeten.
        :param name: Name des Planeten
        :param mass: Masse (kg)
        :param radius: Radius (m)
        :param G_const: Gravitationskonstante
        :param g_const: Oberflächengravitation (m/s²)
        :param height_orbit: Höhe des Zielorbits (m)
        """
        self.name = name
        self.mass = mass
        self.radius = radius
        self.G_const = G_const
        self.g_const = g_const
        self.height_orbit = height_orbit
        self.rotation_period = rotation_period

    @property
    def v_equator(self):
        if hasattr(self, "rotation_period"):
            return 2 * m.pi * self.radius / self.rotation_period
        else:
            return None

    @property
    def v_equator(self):
        """Berechnet die Rotationsgeschwindigkeit am Äquator (m/s)."""
        if hasattr(self, "rotation_period"):
            return 2 * m.pi * self.radius / self.rotation_period
        else:
            return None

    @property
    def v_orbit(self):
        """Berechnet die Kreisbahngeschwindigkeit auf der gewählten Orbit-Höhe (m/s)."""
        return m.sqrt(self.G_const * self.mass / (self.radius + self.height_orbit))
    


class location:
    """
    Modelliert einen Startort.
    """
    def __init__(self, name, latitude_deg, longitude_deg=None, elevation=0):
        """
        Initialisiert einen Startort.
        :param name: Name des Ortes
        :param latitude_deg: Breitengrad (°)
        :param longitude_deg: Längengrad (°)
        :param elevation: Höhe über Meer (m)
        """
        self.name = name
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.elevation = elevation

    def rot_bonus(self, planet):
        """
        Berechnet den Rotationsbonus des Planeten für diesen Startort (m/s).
        :param planet: Planet-Objekt (liefert Äquatorgeschwindigkeit)
        :return: Rotationsbonus (m/s)
        """
        phi = m.radians(self.latitude_deg)
        if planet.v_equator:
            return planet.v_equator * m.cos(phi)
        else:
            return 0
