# Project Title

A 3D satellite orbital mechanics simulation for visualizing Earth satellites with realistic physics.

## Description

OrbitSim is a Python-based tool for simulating and visualizing satellite orbits around Earth. I developed this primarily with the goal of showcasing experience in python programming, an ability to implement physical data and as a way to educate myself in what project development involves. What I ended up learning over the past couple of weeks was really how little I knew before starting, despite being a computer science student, and even more so how little I realize I know now. Applying software development skills to address a problem is a far cry from answering exam questions, and although my courses no doubt set me up for success here, I have realised that the best way to learn is to build. Really the point here is not any of the nice code but rather the ability to learn and apply. I had absolutely 0 knowledge regarding the physics or the libraries in python, but the learning journey has been very enjoyable and truly fascinating. 

This project borrows from sources listed at the bottom of this document to implement TLE reading functionality and uses the data provided in these files in orbital calculations to represent visually using matplotlib. I used CelesTrak for obtaining my TLE files.

### Dependencies

Python 3.8+
Required packages (installable via pip):

numpy (v2.2.3+) -- for numerical calculations --
matplotlib (v3.10.1+) -- for visualization --
contourpy, cycler, fonttools, kiwisolver, packaging, pillow, pyparsing, python-dateutil, six

### Installing

1. Clone repository:
    git clone https://github.com/liamnightingale/OrbitalSim.git
    cd OrbitalSim
2. Install the required dependencies:
   pip install -r requirements.txt


  Project Structure:
orbital-simulation/
├── data/
│   └── MolniyaSATCAT.txt  # Sample TLE data file
├── src/
│   ├── __init__.py        # Package initialization
│   ├── spacecraft.py      # Spacecraft and TLE handling
│   ├── orbital_mechanics.py # Orbital propagation functions
│   ├── planetary_data.py  # Earth and celestial body data
│   └── plotting_tools.py  # Visualization tools
├── examples/
│   ├── tle_example.py     # Example using the package modules
│   └── tle_animation.py   # Standalone TLE animation script
├── requirements.txt       # Required Python packages
└── README.md              # Project documentation

### Executing program
Run the TLE example script to visualize satellite orbits from a TLE file:
   pip install -r requirements.txt

The script will:
1. Load satellites from the TLE file
2. Display orbital information for each satellite
3. Create a 3D visualization of the orbits
4. Generate an animation showing the satellites' motion

Note: You may need to adjust the file path to the TLE data file in the scripts.

Loading satellites from TLE data:
```
from spacecraft import Spacecraft

# Load satellites from a TLE file
satellites = Spacecraft.from_tle_file("path/to/tle_file.txt")

# Display satellite information
for sat in satellites:
    print(f"Satellite: {sat.name}")
    print(f"Semi-major axis: {sat.a:.2f} km")
    print(f"Eccentricity: {sat.e:.6f}")
    print(f"Inclination: {np.degrees(sat.i):.2f}°")
    print(f"Period: {sat.get_period() / 3600:.2f} hours")
```
Creating orbit visualizations:
```
import numpy as np
from plotting_tools import OrbitPlotter
from orbital_mechanics import propagate_orbit

# Create a plotter and add Earth
plotter = OrbitPlotter(figsize=(10, 8))
plotter.plot_earth()

# Create time array for propagation
tspan = np.linspace(0, 24*3600, 500)  # 24 hours, 500 steps

# For each satellite, propagate orbit and add to visualization
for sat in satellites:
    X, Y, Z = propagate_orbit(sat, tspan)
    plotter.add_spacecraft(X, Y, Z, label=sat.name)

# Finalize and display the visualization
plotter.set_equal_aspect()
plotter.add_legend(loc='upper left')
plotter.show()
```

## Help
Common Issues:

1. TLE file not found: Ensure the TLE file path is correct in the script
2. Package imports: If experiencing import errors, verify your Python path includes the project directory

## Authors

Contributors names and contact info

Liam Nightingale  
liam.nightingale.2024@mumail.ie

## Version History

0.1

>Initial development version<
>Basic TLE parsing and visualization capabilities<
>Example scripts for demonstration<

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
     Excellent README template I found.
  
* [PlainEnglish](https://plainenglish.io/blog/plot-satellites-real-time-orbits-with-python-s-matplotlib)
     This got me started down the path of orbital mechais through python. A very straightforward and helpful       
     introduction example for TLE parsing and plotting.
  
* [Alfonso Gonzalez](https://www.youtube.com/@alfonsogonzalez-astrodynam2207)
     This is where I stress again that I DO NOT come from a physics background. This man could explain sand to a    
     beach. Probably my mos useful resource.
  
* [NUIM](https://www.maynoothuniversity.ie)
     I would not be able to comprehend topics in software engineering without a foundational understanding provided 
     through my course.

* [CelesTrak]([https://www.maynoothuniversity.ie](https://celestrak.org/satcat/search.php))
     For obtaining the TLE files which this program uses to plot real objects.
  
