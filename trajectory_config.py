"""
Configuration file for defining custom trajectories for MPC
"""
import numpy as np
from utils import cubic_spline_planner

# Define your waypoints as a list of (x, y) coordinates
# The controller will generate a smooth path through these points

def straight_path():
    """Straight course path like in the original code"""
    ax = [0.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    ay = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    waypoints = list(zip(ax, ay))
    return waypoints

def straight_path2():
    """Slightly curved path like in the original code"""
    ax = [0.0, -10.0, -20.0, -40.0, -50.0, -60.0, -70.0]
    ay = [0.0, -1.0, 1.0, 0.0, -1.0, 1.0, 0.0]
    waypoints = list(zip(ax, ay))
    return waypoints

def forward_path():
    """Forward course path from the original code"""
    ax = [0.0, 60.0, 125.0, 50.0, 75.0, 30.0, -10.0]
    ay = [0.0, 0.0, 50.0, 65.0, 30.0, 50.0, -20.0]
    waypoints = list(zip(ax, ay))
    return waypoints

# Example: Circular path
def circular_path():
    """Circular path - adjusted to match expected waypoint density"""
    radius = 30.0
    center_x, center_y = 50.0, 0.0
    
    # Generate fewer points along a circle - similar to original examples
    angles = np.linspace(0, 2*np.pi, 12)  # Reduced from 20 to have fewer points
    waypoints = [(center_x + radius * np.cos(angle), 
                  center_y + radius * np.sin(angle)) for angle in angles]
    
    return waypoints

# Example: Figure-8 path
def figure_eight_path():
    """Figure-8 path - adjusted to match expected waypoint density"""
    radius = 30.0
    
    # Generate fewer points for the figure-8
    angles = np.linspace(0, 2*np.pi, 16)  # Reduced from 40 to have fewer points
    waypoints = []
    
    for angle in angles:
        # Figure-8 parametric equations
        x = radius * np.cos(angle)
        y = radius/2 * np.sin(2*angle)
        waypoints.append((x, y))
    
    return waypoints

# Example: Slalom path
def slalom_path():
    """Slalom path with fewer points - similar to original examples"""
    waypoints = [
        (0.0, 0.0),
        (20.0, 10.0),
        (40.0, -10.0),
        (60.0, 10.0),
        (80.0, -10.0),
        (100.0, 0.0)
    ]
    return waypoints

# Add your own custom path here!
def my_custom_path():
    # Define your waypoints as a list of (x, y) coordinates
    waypoints = [
        (0.0, 0.0),    # Starting point
        (10.0, 10.0),  # Second point
        (20.0, 0.0),   # Third point
        # Add more points as needed
    ]
    return waypoints

# Dictionary mapping trajectory names to functions
TRAJECTORIES = {
    "Straight": straight_path,
    "Wavy": straight_path2,
    "Spline": forward_path,
    "Circular": circular_path,
    "Eternity": figure_eight_path,
    "Slalom": slalom_path,
    "Custom": my_custom_path,
    # Students can add more here
}

# The default trajectory to use
DEFAULT_TRAJECTORY = "Eternity"