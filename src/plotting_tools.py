"""
plotting_tools.py - Visualization tools for orbital simulations
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

from .planetary_data import Earth, CELESTIAL_BODIES

class OrbitPlotter:
    """Class for creating 3D orbital visualizations"""
    
    def __init__(self, figsize=(10, 8), dpi=100, bg_color='black'):
        """
        Initialize the orbit plotter
        
        Parameters:
            figsize (tuple): Figure size (width, height) in inches
            dpi (int): Dots per inch for the figure
            bg_color (str): Background color for the plot
        """
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor(bg_color)
        
        # Set labels and title
        self.ax.set_xlabel('X (km)')
        self.ax.set_ylabel('Y (km)')
        self.ax.set_zlabel('Z (km)')
        self.ax.set_title('Orbital Visualization')
        self.ax.set_box_aspect([1, 1, 1])
        
        # Stored data for animation
        self.spacecraft_data = []
        self.lines = []
        self.markers = []
        self.animation = None
        
    def plot_earth(self, wireframe=True, alpha=0.5, color='purple'):
        """
        Add Earth to the plot
        
        Parameters:
            wireframe (bool): If True, plot wireframe instead of surface
            alpha (float): Transparency value (0-1)
            color (str): Color of the Earth
        """
        # Get Earth ellipsoid points
        X, Y, Z = Earth.get_ellipsoid_points()
        
        if wireframe:
            self.ax.plot_wireframe(X, Y, Z, color=color, alpha=alpha, linewidth=0.5)
        else:
            self.ax.plot_surface(X, Y, Z, color=color, alpha=alpha)
            
        return self
    
    def plot_body(self, body_name, position=(0, 0, 0), wireframe=True, alpha=0.7):
        """
        Add a celestial body to the plot
        
        Parameters:
            body_name (str): Name of the body (must be in CELESTIAL_BODIES)
            position (tuple): Position of the body center (x, y, z)
            wireframe (bool): If True, plot wireframe instead of surface
            alpha (float): Transparency value (0-1)
        """
        body_name = body_name.lower()
        if body_name not in CELESTIAL_BODIES:
            raise ValueError(f"Unknown celestial body: {body_name}")
            
        body = CELESTIAL_BODIES[body_name]
        
        if body_name == "earth":
            return self.plot_earth(wireframe, alpha)
            
        # Get sphere points for the body
        X, Y, Z = body.get_sphere_points()
        
        # Offset to the correct position
        X += position[0]
        Y += position[1]
        Z += position[2]
        
        if wireframe:
            self.ax.plot_wireframe(X, Y, Z, color=body.color, alpha=alpha, linewidth=0.5)
        else:
            self.ax.plot_surface(X, Y, Z, color=body.color, alpha=alpha)
            
        return self
        
    def plot_orbit(self, X, Y, Z, label=None, color=None, linewidth=1.0):
        """
        Plot a static orbit path
        
        Parameters:
            X, Y, Z (array): Coordinates of the orbit
            label (str): Label for the legend
            color (str): Line color
            linewidth (float): Width of the line
        """
        line, = self.ax.plot(X, Y, Z, label=label, color=color, linewidth=linewidth)
        return line
        
    def add_spacecraft(self, X, Y, Z, label=None, color=None, marker_size=6):
        """
        Add a spacecraft to the animation
        
        Parameters:
            X, Y, Z (array): Position coordinates over time
            label (str): Label for the legend
            color (str): Color for the spacecraft and orbit
            marker_size (float): Size of the marker representing the spacecraft
        """
        # Store spacecraft data for animation
        self.spacecraft_data.append({
            'X': X,
            'Y': Y,
            'Z': Z,
            'label': label,
            'color': color
        })
        
        # Plot the orbit path
        line = self.plot_orbit(X, Y, Z, label=label, color=color)
        self.lines.append(line)
        
        # Create marker for the spacecraft
        marker, = self.ax.plot([X[0]], [Y[0]], [Z[0]], 
                              marker='o', markersize=marker_size,
                              color=color, markerfacecolor=color)
        self.markers.append(marker)
        
        return self
        
    def set_equal_aspect(self):
        """Set equal aspect ratio for the 3D plot"""
        limits = np.array([
            self.ax.get_xlim3d(),
            self.ax.get_ylim3d(),
            self.ax.get_zlim3d()
        ])
        
        origin = np.mean(limits, axis=1)
        radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
        
        self.ax.set_xlim3d([origin[0] - radius, origin[0] + radius])
        self.ax.set_ylim3d([origin[1] - radius, origin[1] + radius])
        self.ax.set_zlim3d([origin[2] - radius, origin[2] + radius])
        
        return self
        
    def create_animation(self, interval=30, frames=None, repeat=True):
        """
        Create an animation of the spacecraft motion
        
        Parameters:
            interval (int): Time between frames in milliseconds
            frames (int): Number of frames to use (defaults to length of data)
            repeat (bool): Whether to repeat the animation
            
        Returns:
            FuncAnimation: The created animation
        """
        if not self.spacecraft_data:
            raise ValueError("No spacecraft data added. Use add_spacecraft() first.")
            
        if frames is None:
            # Use the length of the first spacecraft's data
            frames = len(self.spacecraft_data[0]['X'])
            
        # Animation update function
        def update(frame):
            for i, sat_data in enumerate(self.spacecraft_data):
                self.markers[i].set_data_3d(
                    [sat_data['X'][frame]],
                    [sat_data['Y'][frame]],
                    [sat_data['Z'][frame]]
                )
            return self.markers
            
        # Create the animation
        self.animation = FuncAnimation(
            self.fig, update, frames=frames,
            interval=interval, blit=False, repeat=repeat
        )
        
        return self.animation
        
    def add_legend(self, **kwargs):
        """Add a legend to the plot with customizable parameters"""
        self.ax.legend(**kwargs)
        return self
        
    def show(self):
        """Display the plot or animation"""
        plt.tight_layout()
        plt.show()
        
    def save_animation(self, filename, **kwargs):
        """
        Save the animation to a file
        
        Parameters:
            filename (str): Output filename
            **kwargs: Additional arguments for animation.save()
        """
        if self.animation is None:
            raise ValueError("No animation created. Call create_animation() first.")
            
        self.animation.save(filename, **kwargs)
        return self