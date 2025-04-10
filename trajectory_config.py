"""
Configuration file for defining custom trajectories for MPC
"""

# Define your waypoints as a list of (x, y) coordinates
# The controller will generate a smooth path through these points

# Example: Circular path
def circular_path():
    import numpy as np
    radius = 30.0
    center_x, center_y = 50.0, 0.0
    
    # Generate points along a circle
    angles = np.linspace(0, 2*np.pi, 20)  # 20 points around the circle
    waypoints = [(center_x + radius * np.cos(angle), 
                  center_y + radius * np.sin(angle)) for angle in angles]
    
    return waypoints

# Example: Figure-8 path
def figure_eight_path():
    import numpy as np
    radius = 30.0
    
    # Generate points for a figure-8
    angles = np.linspace(0, 2*np.pi, 40)  # 40 points around the figure-8
    waypoints = []
    
    for angle in angles:
        # Figure-8 parametric equations
        x = radius * np.cos(angle)
        y = radius/2 * np.sin(2*angle)  # Note the 2*angle for figure-8
        waypoints.append((x, y))
    
    return waypoints

# Example: Slalom path
def slalom_path():
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
    "circular": circular_path,
    "figure_eight": figure_eight_path,
    "slalom": slalom_path,
    "custom": my_custom_path,
    # Students can add more here
}

# The default trajectory to use
DEFAULT_TRAJECTORY = "circular"