"""
Orbital simulation package - tools for simulating and visualizing satellite orbits
"""

# Make key classes available directly from the package
from .spacecraft import Spacecraft
from .plotting_tools import OrbitPlotter
from .orbital_mechanics import propagate_orbit
from .planetary_data import Earth, CELESTIAL_BODIES

# Define package metadata