import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta

def plot_tle_animation(tle_filename):

    # ------------------ 1) READ AND PARSE TLE DATA ------------------
    with open(tle_filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    # Collect valid TLE pairs
    satellite_TLEs = []
    idx = 0
    while idx < len(lines) - 1:
        if lines[idx].startswith('1') and lines[idx+1].startswith('2'):
            satellite_TLEs.append((lines[idx], lines[idx+1]))
            idx += 2
        else:
            idx += 1
    # ------------------ 2) SETUP FIGURE FOR 3D ANIMATION ------------------
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('Satellite Orbits Animation')
    ax.set_box_aspect([1,1,1])

    u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:30j]
    rx = 6378
    ry = 6378
    rz = 6356

    ax.plot_wireframe(rx*np.cos(u)*np.sin(v),
                      ry*np.sin(u)*np.sin(v),
                      rz*np.cos(v),color="purple",
                      alpha=0.5,lw = 0.5, zorder=0)
    
    #print((r*np.cos(u)[0,0]*np.sin(v)[0,0],
      # r*np.sin(u)[0,0]*np.sin(v)[0,0],
      # r*np.cos(v)[0,0]))

    # Data structure to hold satellite parameters and computed positions
    satellites = []

    # Earth’s gravitational parameter
    mu_earth = 398600.4418  # [km^3/s^2]

    # ------------------ 3) PARSE TLE LINES & ORBITAL ELEMENTS ------------------
    for line1, line2 in satellite_TLEs:

        # Use satellite catalog number or a substring as "name"
        sat_name = line2[2:7].strip()

        # 3.1) Parse epoch from line 1
        epoch_year = int(line1[18:20])
        epoch_dayFrac = float(line1[20:32])

        # Determine the full year
        if epoch_year < 57:
            year_full = 2000 + epoch_year
        else:
            year_full = 1900 + epoch_year

        # Approximate epoch as Python datetime
        # day-of-year 1 => Jan 1, so subtract 1 then add days
        epoch_dt = datetime(year_full, 1, 1) + timedelta(days=(epoch_dayFrac - 1))

        # 3.2) Parse orbital elements from line 2
        inc_deg = float(line2[8:16])
        raan_deg = float(line2[17:25])
        ecc_str = "0." + line2[26:33].strip()
        ecc = float(ecc_str)
        argp_deg = float(line2[34:42])
        M0_deg = float(line2[43:51])
        mean_motion = float(line2[52:63])  # rev/day

        # 3.3) Mean motion (rad/sec)
        n_radSec = mean_motion * 2.0 * np.pi / 86400.0  # 24*3600 = 86400

        # 3.4) Semi-major axis [km] from mean motion in 2-body approximation
        a = (mu_earth / (n_radSec**2)) ** (1.0/3.0)

        # Store data
        satellites.append({
            'name':     sat_name,
            'epoch':    epoch_dt,
            'a':        a,
            'e':        ecc,
            'i':        np.radians(inc_deg),
            'RAAN':     np.radians(raan_deg),
            'omega':    np.radians(argp_deg),
            'M0':       np.radians(M0_deg),
            'n':        n_radSec
        })

    # ------------------ 4) PRE-COMPUTE ORBITAL POSITIONS ------------------
    # For a simple animation, let's compute (X,Y,Z) for a couple of orbits.

    num_sats = len(satellites)
    # Find the maximum orbital period among satellites
    periods = [(2.0*np.pi) / sat['n'] for sat in satellites]
    max_T = max(periods)

    # Number of steps for the animation
    num_steps = 500
    # We'll animate up to 2 orbits of the "slowest" satellite
    tspan = np.linspace(0, 2*max_T, num_steps)

    # Pre-allocate position arrays
    for sat in satellites:
        sat['X'] = np.zeros(num_steps)
        sat['Y'] = np.zeros(num_steps)
        sat['Z'] = np.zeros(num_steps)

    # Compute positions at each time step
    for k in range(num_steps):
        tk = tspan[k]
        for sat in satellites:
            # Mean anomaly at time tk
            M = sat['M0'] + sat['n'] * tk

            # Solve for Eccentric Anomaly E using Newton-Raphson
            E = M
            for _ in range(10):
                E = E - (E - sat['e']*np.sin(E) - M) / (1 - sat['e']*np.cos(E))

            # True anomaly
            nu = 2.0 * np.arctan2(
                np.sqrt(1+sat['e']) * np.sin(E/2),
                np.sqrt(1-sat['e']) * np.cos(E/2)
            )

            # Orbital radius
            r_orbit = sat['a'] * (1 - sat['e']*np.cos(E))

            # Position in perifocal coordinates
            x_orb = r_orbit * np.cos(nu)
            y_orb = r_orbit * np.sin(nu)
            z_orb = 0.0

            # Rotation to ECI
            RAAN = sat['RAAN']
            inc  = sat['i']
            w    = sat['omega']

            # Note: Rz(-RAAN)*Rx(-i)*Rz(-omega) => equivalently
            #       R3_W' * R1_i' * R3_w'
            # Build each rotation (transposed, i.e. inverse)
            R3_W = np.array([
                [ np.cos(RAAN),  np.sin(RAAN), 0],
                [-np.sin(RAAN),  np.cos(RAAN), 0],
                [           0,             0, 1]
            ])
            R1_i = np.array([
                [1,          0,           0],
                [0,  np.cos(inc),  np.sin(inc)],
                [0, -np.sin(inc),  np.cos(inc)]
            ])
            R3_w = np.array([
                [ np.cos(w),  np.sin(w), 0],
                [-np.sin(w),  np.cos(w), 0],
                [         0,          0, 1]
            ])

            Q = R3_W.T @ R1_i.T @ R3_w.T
            rECI = Q @ np.array([x_orb, y_orb, z_orb])

            sat['X'][k] = rECI[0]
            sat['Y'][k] = rECI[1]
            sat['Z'][k] = rECI[2]

    # ------------------ 5) PREPARE PLOTS FOR ANIMATION ------------------
    colors = plt.cm.tab10(np.linspace(0,1,num_sats))  # or use any colormap
    orbit_lines = []
    sat_markers = []

    for i, sat in enumerate(satellites):
        # Plot full orbit (static)
        line, = ax.plot(sat['X'], sat['Y'], sat['Z'],
                        color=colors[i], linewidth=1, label=sat['name'])
        orbit_lines.append(line)

        # Plot marker for current position
        marker, = ax.plot([sat['X'][0]], [sat['Y'][0]], [sat['Z'][0]],
                          marker='o', markersize=6,
                          color=colors[i], markerfacecolor=colors[i])
        sat_markers.append(marker)

    ax.legend(loc='upper left')


    def set_aspect_equal_3d(ax):
     x_limits = ax.get_xlim3d()
     y_limits = ax.get_ylim3d()
     z_limits = ax.get_zlim3d()

     x_range = x_limits[1] - x_limits[0]
     y_range = y_limits[1] - y_limits[0]
     z_range = z_limits[1] - z_limits[0]
     max_range = max(x_range, y_range, z_range)

     mid_x = 0.5 * (x_limits[0] + x_limits[1])
     mid_y = 0.5 * (y_limits[0] + y_limits[1])
     mid_z = 0.5 * (z_limits[0] + z_limits[1])

     ax.set_xlim3d([mid_x - max_range/2, mid_x + max_range/2])
     ax.set_ylim3d([mid_y - max_range/2, mid_y + max_range/2])
     ax.set_zlim3d([mid_z - max_range/2, mid_z + max_range/2])

    # ------------------ 6) ANIMATION FUNCTION ------------------
    def update(frame):
        # Update marker positions at time = frame
        for i, sat in enumerate(satellites):
            sat_markers[i].set_data_3d(
                [sat['X'][frame]], 
                [sat['Y'][frame]],
                [sat['Z'][frame]]
            )
        return sat_markers

    # Create animation
    ani = FuncAnimation(fig, update, frames=num_steps,
                        interval=30, blit=False, repeat=True)
    #plt.tight_layout()
    set_aspect_equal_3d(ax)
    plt.show()


if __name__ == "__main__":
    # Adjust to your actual TLE filename:
    TLE_FILENAME = r'C:\Users\liamn\OneDrive\Documents\CodingProjects\OrbitSim\data\MolniyaSATCAT.txt'
    
    plot_tle_animation(TLE_FILENAME)
