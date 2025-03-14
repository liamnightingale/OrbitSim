"""
orbital_mechanics.py - Orbital mechanics calculations and propagation
"""

import numpy as np

def solve_kepler(M, e, tolerance=1e-8, max_iterations=10):
    """
    Solve Kepler's equation for eccentric anomaly
    
    Parameters:
        M (float): Mean anomaly in radians
        e (float): Eccentricity
        tolerance (float): Error tolerance for convergence
        max_iterations (int): Maximum number of iterations
        
    Returns:
        float: Eccentric anomaly in radians
    """
    # Initial guess
    if e < 0.8:
        E = M  # For low eccentricity, M is a good initial guess
    else:
        E = np.pi  # For high eccentricity, pi is a better initial guess
    
    # Newton-Raphson iteration
    for i in range(max_iterations):
        E_new = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        if abs(E_new - E) < tolerance:
            return E_new
        E = E_new
    
    # Return best estimate even if not fully converged
    return E

def true_anomaly_from_eccentric(E, e):
    """
    Calculate true anomaly from eccentric anomaly
    
    Parameters:
        E (float): Eccentric anomaly in radians
        e (float): Eccentricity
        
    Returns:
        float: True anomaly in radians
    """
    return 2.0 * np.arctan2(
        np.sqrt(1.0 + e) * np.sin(E / 2.0),
        np.sqrt(1.0 - e) * np.cos(E / 2.0)
    )

def orbital_radius(a, e, E):
    """
    Calculate orbital radius at a given eccentric anomaly
    
    Parameters:
        a (float): Semi-major axis
        e (float): Eccentricity
        E (float): Eccentric anomaly in radians
        
    Returns:
        float: Orbital radius
    """
    return a * (1.0 - e * np.cos(E))

def perifocal_to_eci(r_perifocal, RAAN, inc, omega):
    """
    Transform from perifocal to Earth-Centered Inertial (ECI) coordinates
    
    Parameters:
        r_perifocal (ndarray): Position vector in perifocal frame [x, y, z]
        RAAN (float): Right Ascension of Ascending Node in radians
        inc (float): Inclination in radians
        omega (float): Argument of periapsis in radians
        
    Returns:
        ndarray: Position vector in ECI frame [x, y, z]
    """
    # Rotation matrices
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
        [ np.cos(omega),  np.sin(omega), 0],
        [-np.sin(omega),  np.cos(omega), 0],
        [         0,          0, 1]
    ])
    
    # Combined rotation matrix (transposed for inverse transformation)
    Q = R3_W.T @ R1_i.T @ R3_w.T
    
    # Transform the position vector
    return Q @ r_perifocal

def propagate_orbit(spacecraft, time_array):
    """
    Propagate orbital motion for a spacecraft over a time array
    
    Parameters:
        spacecraft: Spacecraft object with orbital elements
        time_array (ndarray): Array of times in seconds from epoch
        
    Returns:
        tuple: (X, Y, Z) arrays of positions in ECI frame
    """
    # Pre-allocate position arrays
    n_steps = len(time_array)
    X = np.zeros(n_steps)
    Y = np.zeros(n_steps)
    Z = np.zeros(n_steps)
    
    # Extract orbital elements
    a = spacecraft.a
    e = spacecraft.e
    inc = spacecraft.i
    RAAN = spacecraft.RAAN
    omega = spacecraft.omega
    M0 = spacecraft.M0
    n = spacecraft.n
    
    # Compute positions at each time step
    for k in range(n_steps):
        t = time_array[k]
        
        # Mean anomaly at time t
        M = M0 + n * t
        
        # Solve for eccentric anomaly
        E = solve_kepler(M, e)
        
        # Calculate true anomaly
        nu = true_anomaly_from_eccentric(E, e)
        
        # Calculate orbital radius
        r = orbital_radius(a, e, E)
        
        # Position in perifocal coordinates
        r_perifocal = np.array([
            r * np.cos(nu),
            r * np.sin(nu),
            0.0
        ])
        
        # Transform to ECI
        r_eci = perifocal_to_eci(r_perifocal, RAAN, inc, omega)
        
        # Store positions
        X[k] = r_eci[0]
        Y[k] = r_eci[1]
        Z[k] = r_eci[2]
    
    return X, Y, Z 