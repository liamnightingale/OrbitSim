"""
spacecraft.py - Spacecraft handling and TLE processing module
"""

import numpy as np
from datetime import datetime, timedelta

class Spacecraft:
    """Class representing a spacecraft or satellite defined by TLE data"""
    
    # Earth's gravitational parameter (km^3/s^2)
    MU_EARTH = 398600.4418
    
    def __init__(self, name="Unknown", tle_line1=None, tle_line2=None):
        """
        Initialize a spacecraft from TLE data
        
        Parameters:
            name (str): Name of the spacecraft
            tle_line1 (str): First line of the TLE
            tle_line2 (str): Second line of the TLE
        """
        self.name = name
        
        # Initialize orbital elements
        self.a = 0.0         # Semi-major axis (km)
        self.e = 0.0         # Eccentricity
        self.i = 0.0         # Inclination (rad)
        self.RAAN = 0.0      # Right Ascension of Ascending Node (rad)
        self.omega = 0.0     # Argument of Periapsis (rad)
        self.M0 = 0.0        # Mean Anomaly at epoch (rad)
        self.n = 0.0         # Mean motion (rad/sec)
        self.epoch = None    # Epoch as datetime
        
        # If TLE data is provided, parse it
        if tle_line1 and tle_line2:
            self.parse_tle(tle_line1, tle_line2)
            
    def parse_tle(self, line1, line2):
        """
        Parse TLE lines and compute orbital elements
        
        Parameters:
            line1 (str): First line of the TLE
            line2 (str): Second line of the TLE
        """
        # Use satellite catalog number if name isn't set
        if self.name == "Unknown":
            self.name = line2[2:7].strip()
            
        # Parse epoch from line 1
        epoch_year = int(line1[18:20])
        epoch_dayFrac = float(line1[20:32])
        
        # Determine the full year
        if epoch_year < 57:  # Arbitrary cutoff for 21st century
            year_full = 2000 + epoch_year
        else:
            year_full = 1900 + epoch_year
            
        # Calculate epoch as Python datetime
        self.epoch = datetime(year_full, 1, 1) + timedelta(days=(epoch_dayFrac - 1))
        
        # Parse orbital elements from line 2
        inc_deg = float(line2[8:16])
        raan_deg = float(line2[17:25])
        ecc_str = "0." + line2[26:33].strip()
        self.e = float(ecc_str)
        argp_deg = float(line2[34:42])
        M0_deg = float(line2[43:51])
        mean_motion = float(line2[52:63])  # rev/day
        
        # Convert to radians and standard units
        self.i = np.radians(inc_deg)
        self.RAAN = np.radians(raan_deg)
        self.omega = np.radians(argp_deg)
        self.M0 = np.radians(M0_deg)
        
        # Mean motion in rad/sec
        self.n = mean_motion * 2.0 * np.pi / 86400.0  # 24*3600 = 86400
        
        # Calculate semi-major axis from mean motion
        self.a = (self.MU_EARTH / (self.n**2)) ** (1.0/3.0)
        
    def get_period(self):
        """Return orbital period in seconds"""
        return 2.0 * np.pi / self.n
        
    def __str__(self):
        """String representation of the spacecraft"""
        return f"Spacecraft: {self.name}, a={self.a:.1f} km, e={self.e:.4f}, i={np.degrees(self.i):.1f}°"
        
    @staticmethod
    def from_tle_file(filename):
        """
        Create a list of Spacecraft objects from a TLE file
        
        Parameters:
            filename (str): Path to the TLE file
            
        Returns:
            list: List of Spacecraft objects
        """
        satellites = []
        
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        
        # Collect valid TLE pairs
        idx = 0
        while idx < len(lines) - 1:
            if lines[idx].startswith('1') and lines[idx+1].startswith('2'):
                sat = Spacecraft(tle_line1=lines[idx], tle_line2=lines[idx+1])
                satellites.append(sat)
                idx += 2
            else:
                idx += 1
                
        return satellites