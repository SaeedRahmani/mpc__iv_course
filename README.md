# Model Predictive Control with Custom Trajectories

This project allows you to test Model Predictive Control (MPC) algorithms on custom trajectories for autonomous vehicle path tracking.

## Getting Started

### Prerequisites

This project requires Python 3.6+ and the following libraries:
- numpy
- scipy
- matplotlib
- cvxpy (for solving optimization problems)

Install these dependencies using pip:

```bash
pip install numpy scipy matplotlib cvxpy
```

### File Structure

```
.
├── README.md
├── trajectory_config.py      # Define custom trajectories here
├── mpc_with_custom_trajectory.py  # Command-line version
├── mpc_trajectory_gui.py     # GUI version (optional)
├── PathPlanning/
│   └── CubicSpline/
│       └── cubic_spline_planner.py
├── PathTracking/
│   └── model_predictive_speed_and_steer_control/
│       └── model_predictive_speed_and_steer_control.py
└── utils/
    └── angle.py
```

## Usage Options

### Option 1: Using Command Line

Run the command-line version to test predefined trajectories:

```bash
python mpc_with_custom_trajectory.py --trajectory circular --speed 10.0
```

Available options:
- `--trajectory` or `-t`: Choose from predefined trajectories (`circular`, `figure_eight`, `slalom`, `custom`)
- `--speed` or `-s`: Target speed in m/s
- `--dl`: Distance between interpolated points
- `--no-animation`: Disable animation for faster computation

### Option 2: Using the GUI (Recommended for Students)

Run the GUI version for interactive trajectory design:

```bash
python mpc_trajectory_gui.py
```

With the GUI, you can:
- Select predefined trajectories
- Create custom trajectories by clicking on the plot
- Set simulation parameters
- Run the MPC simulation with your custom trajectory

## Creating Your Own Trajectories

### Method 1: Editing the Configuration File

Open `trajectory_config.py` and add your own function that returns a list of (x, y) waypoints:

```python
def my_custom_path():
    waypoints = [
        (0.0, 0.0),    # Starting point
        (10.0, 10.0),  # Second point
        (20.0, 0.0),   # Third point
        # Add more points as needed
    ]
    return waypoints

# Add your function to the TRAJECTORIES dictionary
TRAJECTORIES["my_custom"] = my_custom_path
```

### Method 2: Using the GUI

1. Click on the plot to add waypoints
2. Click "Use Custom Points" to save your trajectory
3. Click "Run Simulation" to test your trajectory with MPC

## Understanding the MPC Parameters

The MPC controller has several parameters that affect performance:

- **Prediction Horizon (T)**: How far ahead the controller predicts (default: 5 steps)
- **Cost Matrices (Q, R, Rd)**: Weights for state tracking error, control input, and input changes
- **Time Step (DT)**: Simulation time step (default: 0.2s)
- **Vehicle Parameters**: Wheelbase, max steering angle, max acceleration, etc.

These can be modified in the original MPC implementation file if needed.

## Tips for Successful Trajectories

1. **Smoothness**: The cubic spline will create a smooth path, but waypoints that are too close or have sharp angles may cause issues
2. **Feasibility**: Consider the vehicle's physical constraints (max steering angle, acceleration limits)
3. **Complexity**: Start with simple trajectories and gradually increase complexity
4. **Speed Profile**: The default speed profile is constant, but you can experiment with variable speeds

## Analyzing Results

The simulation outputs:
- Tracking performance (reference vs. actual path)
- Speed profile over time
- Control inputs (acceleration and steering angle)

Look for:
- How closely the vehicle follows the reference path
- If the vehicle respects its physical constraints
- Where the controller struggles (tight curves, etc.)

## Troubleshooting

- **Solver Errors**: May indicate an infeasible trajectory or constraints
- **Slow Simulation**: Try using `--no-animation` flag for faster computation
- **Path Following Issues**: Check if waypoints are reasonable for the vehicle constraints

Good luck with your MPC experiments!