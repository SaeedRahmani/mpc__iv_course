# Model Predictive Control with Custom Trajectories

This project allows you to test Model Predictive Control (MPC) algorithms on custom trajectories for autonomous vehicle path tracking. It features both a command-line interface and a graphical user interface for trajectory design and MPC parameter tuning.

## Getting Started
Install miniconda using the instructions here: https://www.anaconda.com/docs/getting-started/miniconda/install

### Setting up your conda environment (miniconda is recommended for easy package management)

- Search Anaconda Prompt on Windows (or use a normal terminal on Ubuntu and Mac)
- Run the following codes in Anaconda Prompt or terminal:

```bash
conda create -n ivcourse python=3.12
conda activate ivcourse
```
- The above lines first make a new virtual environment for your project, called "ivcourse." This makes sure that any package that you install, is installed separated from other projects on your system.

### Prerequisites

This project was tested on Python 3.10+ and requires the following libraries:
- numpy
- scipy
- matplotlib
- cvxpy (for solving optimization problems)
- tkinter (for the GUI)

### Install the above dependencies using pip:
- Make sure that the ivcourse environment is activated (conda activate ivcourse)
- run the following (if pip does not work, use pip3)
```bash
pip install -r requirements.txt
# OR if you cannot fine the requirements.txt file, copy the following line and press enter in the Anaconda Prompt or your terminal
# pip install numpy scipy matplotlib cvxpy tkinter
```

Note: tkinter is usually included with Python installations, but if needed:
```bash
# For Ubuntu/Debian
sudo apt-get install python3-tk

# For macOS (with Homebrew)
brew install python-tk

# For Windows (if not already included)
# Typically included by default. If missing:
pip install tk
# Or reinstall Python with the "tcl/tk and IDLE" option checked
```

### File Structure
Make sure that you aer always in the root folder, which means that you are at the highest level folder and not inside the sub-folders. to know where you are, in Anaconda Prompt or Windows Terminal write "dir". You can use "cd" command to change folders. For example, "cd .." goes one level up and " cd FOLDER_NAME" goes to the folder that has the name FOLDER_NAME.

```
.
├── trajectory_config.py        # Define custom trajectories here
├── mpc.py                      # Core MPC implementation
├── run_gui.py                  # Entry point for the GUI application
├── README.md                   # This file
├── requirements.txt            # For installing the dependencies
├── gui/                        # GUI module directory. You won't need it probably
│   ├── __init__.py             # Package initialization
│   └── gui.py                  # Main GUI implementation
├── utils/                      # Utility functions. You won't need it probably
│   ├── angle.py                # Angle manipulation utilities
│   ├── cubic_spline_planner.py # Cubic spline implementation
│   └── plot.py                 # Plotting utilities
```

## Usage Options

### Option 1: Using the GUI (Recommended)

Run the GUI version for interactive trajectory design and MPC parameter tuning: (if python does not work, use python3)

```bash
python run_gui.py
# python3 run_gui.py
```

The GUI application follows a modular design:
- `run_gui.py`: Entry point for launching the application
- `gui/gui.py`: Contains the actual GUI implementation
- `gui/__init__.py`: Makes the GUI components easily importable

With the GUI, you can:
- Select from predefined trajectories
- Create custom trajectories by clicking on the plot
- Configure trajectory generation parameters
- Tune MPC controller parameters
- Adjust vehicle constraints
- Run simulations and visualize results
- View simulation logs

### Option 1: Using Command Line

Run the command-line version to test predefined trajectories with your MPC implementation: (or use python3)

```bash
python mpc.py --trajectory circular --speed 10.0
#python3 mpc.py --trajectory circular --speed 10.0
```

Available options:
- `--trajectory` or `-t`: Choose from predefined trajectories (`Straight`, `Wavy`, `Spline`, `Circular`, `Eternity`, `Slalom`, `Custom`)
- `--speed` or `-s`: Target speed in km/h (default: 10.0)
- `--dl`: Distance between interpolated points (default: 1.0)
- `--no-animation`: Disable animation for faster computation

## Creating Your Own Trajectories

### Method 1: Using the GUI (Recommended)

1. Launch the GUI by running `python run_gui.py` (when you are in the root directory of the project.)
2. In the Trajectory tab, select "Custom" from the dropdown
3. Click "Clear Points" to start fresh
4. Click on the plot area to place waypoints for your custom trajectory
   - The plot area is fixed from -100 to 100 in both x and y coordinates
5. When you've finished adding points, click "Use These Points"
6. Optional: At each time, click "Update Preview" to see the spline trajectory
7. Click "Run Simulation" to test your trajectory with the MPC controller
8. What do you observe? Try to improve the performance of the trajectory following by changing both the parameters of MPC and reference trajectory
9. What is the effect of vehicle parameters?

### Method 2: Editing the Configuration File (More advanced and flexible)

Open `trajectory_config.py` and add your own function that returns a list of (x, y) waypoints:

```python
def my_custom_trajectory():
    # Define your waypoints as a list of (x, y) coordinates
    waypoints = [
        (0.0, 0.0),    # Starting point
        (10.0, 10.0),  # Second point
        (20.0, 0.0),   # Third point
        # Add more points as needed
    ]
    return waypoints

# Add your function to the TRAJECTORIES dictionary
TRAJECTORIES["my_custom"] = my_custom_trajectory
```

## Tuning MPC Parameters

The GUI provides comprehensive options for tuning the MPC controller:

### MPC Parameters Tab
- **Prediction and Control**
  - Prediction Horizon (T): Number of prediction steps
  - Time Step (DT): Simulation time step
  - Max Iterations: Maximum iterations for the MPC optimization

- **Cost Matrices**
  - State Cost Matrix (Q): Weights for state tracking error
    - Q1: x position error weight
    - Q2: y position error weight
    - Q3: velocity error weight
    - Q4: yaw error weight
  - Input Cost Matrix (R): Weights for control input magnitudes
    - R1: acceleration input weight
    - R2: steering input weight
  - Input Difference Cost Matrix (Rd): Weights for control input changes
    - Rd1: acceleration change weight
    - Rd2: steering change weight

### Vehicle Parameters Tab
- **Vehicle Constraints**
  - Max Steering Angle: Maximum steering angle in degrees
  - Max Steering Speed: Maximum steering angle change rate in degrees/s
  - Max Speed: Maximum vehicle speed in km/h
  - Max Acceleration: Maximum acceleration in m/s²

- **Vehicle Physical Properties**
  - Wheelbase (WB): Distance between front and rear axles in meters

## Understanding the MPC Algorithm

The implemented MPC controller uses:
- A kinematic bicycle model for vehicle dynamics
- Linearization of the bicycle model for efficient optimization
- Iterative optimization to handle nonlinearities
- CVXPY with the CLARABEL solver for solving the optimization problem (check what is the effect of solver on the performance)

The cost function includes:
- Tracking error costs (position, velocity, orientation)
- Control input costs (acceleration, steering)
- Control rate costs (changes in acceleration and steering)

## Analyzing Results

The simulation outputs:
- Trajectory tracking visualization
- Speed profile over time 
- Steering angles over time 
- Simulation logs with performance metrics (what is missing? Can you add it?)

The log tab in the GUI provides detailed information about:
- Applied MPC and vehicle parameters
- Simulation time and speed
- Maximum steering angles used
- Any errors encountered during simulation

## Troubleshooting

- **Solver Errors**: These may indicate an infeasible trajectory or too aggressive constraints
  - Try changing the target speed
  - Change the prediction horizon
  - Adjust the cost weights to prioritize different aspects

- **Slow Simulation**: For faster execution:
  - Reduce the prediction horizon (T) -- But be aware of the effects 
  - Increase the time step (DT)

- **Path Following Issues**: If the vehicle struggles to follow the path:
  - Increase position weights (Q1, Q2) in the cost matrix
  - Reduce the target speed
  - Ensure the trajectory doesn't have overly tight turns relative to the vehicle constraints
  - Adjust the steering weights to allow more aggressive steering

## License

This project is provided for educational purposes. Is is developed and maintained by Saeed Rahmani (https://github.com/SaeedRahmani)

## Acknowledgments

- Original MPC implementation by Atsushi Sakai (@Atsushi_twi)
- Based on the PythonRobotics repository
