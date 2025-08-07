import numpy as np
from scipy.integrate import odeint
import sympy as sm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

w_0 = float(input('Eigenfrequenz:'))
w = float(input('Erregerfrequenz:'))
t = sm.symbols('t')
m, k = sm.symbols('m k', positive = True)

x = sm.symbols('x', cls=sm.Function) # sm.function macht x zu einer funktion: ort in abhängigkeit der zeit
x = x(t)

dx_dt = sm.diff(x, t)           #Geschiwnditgkeit
d2x_d2t = sm.diff(x, t, t)     #Beschleunigung

# Anfangswerte und k,m
Anfangs_x = float(input('Anfangsort: '))
Anfangs_v = float(input('Anfangsgeschwindigkeit: '))
Anfangswerte = [Anfangs_x, Anfangs_v]
k_wert = float(input('Reibung:'))
m_wert= 1 #input('masse:')

# System der DGLs erster ordnung

Zeitpunkte = np.linspace(0, 20, 1000)

# System der DGLs erster Ordnung
# d²x/dt² + dx/dt + x = 0
def DGL_system(y, t):
    x, dxdt = y
    d2xdt2 = -k_wert*dxdt - (w_0**2)*x + np.cos((w)*t)
    return [dxdt, d2xdt2]

# Numerische Lösung
Lösung = odeint(DGL_system, Anfangswerte, Zeitpunkte)


ort = Lösung[:, 0]
geschwindigkeit = Lösung[:, 1]


# Plot setup
fig, ax = plt.subplots()
ax.set_xlim(0, Zeitpunkte[-1])
ax.set_ylim(np.min(ort)*1.1, np.max(ort)*1.1)
linie, = ax.plot([], [], lw=2)
punkt, = ax.plot([], [], 'ro')
ax.hlines(y=0, xmin=0, xmax=20, colors='black', linestyles='dashed', alpha=0.8,zorder=11)

# Weg mit den scheiß achsen ticks
ax.xaxis.set_tick_params(labelbottom=False)
ax.yaxis.set_tick_params(labelleft=False)
for tick in ax.yaxis.get_major_ticks():
    tick.tick1line.set_visible(False)
    tick.tick2line.set_visible(False)
    tick.label1.set_visible(False)
    tick.label2.set_visible(False)
for tick in ax.xaxis.get_major_ticks():
    tick.tick1line.set_visible(False)
    tick.tick2line.set_visible(False)
    tick.label1.set_visible(False)
    tick.label2.set_visible(False)
ax.grid(True)


# Init function
def init():
    linie.set_data([], [])
    punkt.set_data([], [])
    return linie, punkt

def update(frame):
    if frame == 0:
        # Use sequences even for the first point
        linie.set_data([Zeitpunkte[0]], [ort[0]])  # dummy initial point as a list
        punkt.set_data([Zeitpunkte[0]], [ort[0]])  # pass sequences (lists or arrays)
    else:
        x_data = Zeitpunkte[:frame]
        y_data = ort[:frame]
        linie.set_data(x_data, y_data)
        punkt.set_data([Zeitpunkte[frame-1]], [ort[frame-1]])  # pass a list for the point
    return linie, punkt

# Animation
ani = FuncAnimation(fig, update, frames=len(Zeitpunkte), init_func=init, blit=False, interval=0.01)

plt.show()


plt.close()