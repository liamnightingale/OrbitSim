"""
planetary_data.py - Data for Earth and other celestial bodies
"""

import numpy as np

class Earth:
    """Earth physical and orbital parameters"""
    
    # Physical parameters
    RADIUS_EQUATORIAL = 6378.137  # km
    RADIUS_POLAR = 6356.752  # km
    FLATTENING = 1/298.257223563
    MU = 398600.4418  # km³/s²
    J2 = 0.00108263
    
    # Rotation
    ROTATION_PERIOD = 86164.1  # seconds (sidereal day)
    ANGULAR_VELOCITY = 2.0 * np.pi / ROTATION_PERIOD  # rad/s
    
    @staticmethod
    def get_ellipsoid_points(u_points=40, v_points=30):
        """
        Generate points for plotting Earth as an ellipsoid
        
        Parameters:
            u_points (int): Number of points in u direction (longitude)
            v_points (int): Number of points in v direction (latitude)
            
        Returns:
            tuple: (X, Y, Z) coordinates of ellipsoid points
        """
        u = np.linspace(0, 2 * np.pi, u_points)
        v = np.linspace(0, np.pi, v_points)
        
        X = Earth.RADIUS_EQUATORIAL * np.outer(np.cos(u), np.sin(v))
        Y = Earth.RADIUS_EQUATORIAL * np.outer(np.sin(u), np.sin(v))
        Z = Earth.RADIUS_POLAR * np.outer(np.ones_like(u), np.cos(v))
        
        return X, Y, Z

class CelestialBody:
    """Base class for celestial bodies"""
    
    def __init__(self, name, radius, mu, color="white"):
        """
        Initialize a celestial body
        
        Parameters:
            name (str): Name of the body
            radius (float): Radius in km
            mu (float): Gravitational parameter in km³/s²
            color (str): Color for plotting
        """
        self.name = name
        self.radius = radius
        self.mu = mu
        self.color = color
    
    def get_sphere_points(self, resolution=20):
        """
        Generate points for plotting the body as a sphere
        
        Parameters:
            resolution (int): Number of points in each direction
            
        Returns:
            tuple: (X, Y, Z) coordinates of sphere points
        """
        u, v = np.mgrid[0:2*np.pi:resolution*1j, 0:np.pi:resolution*1j]
        x = self.radius * np.cos(u) * np.sin(v)
        y = self.radius * np.sin(u) * np.sin(v)
        z = self.radius * np.cos(v)
        return x, y, z

# Define some common celestial bodies
MOON = CelestialBody("Moon", 1737.4, 4902.8, "gray")
SUN = CelestialBody("Sun", 695700.0, 1.32712440018e11, "yellow")

# Dictionary of all available bodies
CELESTIAL_BODIES = {
    "earth": Earth,
    "moon": MOON,
    "sun": SUN
}