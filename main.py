"""
tle_example.py - Example showing how to work with TLE files in the orbital simulation
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add the parent directory to the path to import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.spacecraft import Spacecraft
from src.orbital_mechanics import propagate_orbit
from src.plotting_tools import OrbitPlotter

def main():
    # Path to the TLE file
    tle_file = "data/MolniyaSATCAT.txt"
    
    # Check if the file exists
    if not os.path.exists(tle_file):
        print(f"TLE file not found: {tle_file}")
        print("Please make sure the file is in the correct location.")
        return
    
    # Load the TLE data
    satellites = Spacecraft.from_tle_file(tle_file)
    
    # Print information about the loaded satellites
    print(f"Loaded {len(satellites)} satellites from {tle_file}")
    print("\nSatellite Information:")
    print("-" * 60)
    
    for i, sat in enumerate(satellites):
        period_hours = sat.get_period() / 3600  # Convert seconds to hours
        print(f"{i+1}. {sat.name}:")
        print(f"   Semi-major axis: {sat.a:.1f} km")
        print(f"   Eccentricity: {sat.e:.6f}")
        print(f"   Inclination: {np.degrees(sat.i):.2f}°")
        print(f"   Period: {period_hours:.2f} hours")
        print()
    
    # Create an orbit plotter
    plotter = OrbitPlotter(figsize=(12, 10))
    
    # Add Earth
    plotter.plot_earth(alpha=0.5)
    
    # Define duration for visualization (in seconds)
    # Use twice the period of the longest-period satellite
    max_period = max(sat.get_period() for sat in satellites)
    duration = 2 * max_period
    
    # Number of steps for propagation
    num_steps = 500
    
    # Create time array
    tspan = np.linspace(0, duration, num_steps)
    
    # Colors for the different satellites
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
    
    # Add each satellite to the visualization
    for i, sat in enumerate(satellites):
        # Set color (cycling through the color list if needed)
        color = colors[i % len(colors)]
        
        # Propagate orbit
        X, Y, Z = propagate_orbit(sat, tspan)
        
        # Add to plotter
        plotter.add_spacecraft(X, Y, Z, label=sat.name, color=color)
    
    # Add a legend
    plotter.add_legend(loc='upper left')
    
    # Set equal aspect ratio for better visualization
    plotter.set_equal_aspect()
    
    # Create and show the animation
    print("Creating animation...")
    animation = plotter.create_animation(interval=30)
    
    print("Displaying animation. Close the window to exit.")
    plotter.show()

if __name__ == "__main__":
    main()