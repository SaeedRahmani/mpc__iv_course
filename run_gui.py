"""
Run the MPC trajectory GUI application
"""
import tkinter as tk
import sys
import pathlib

# Add the parent directory to the path
sys.path.append(str(pathlib.Path(__file__).parent))

# Import the GUI class
from gui.gui import MPCTrajectoryGUI

def main():
    """Launch the MPC Trajectory Designer GUI"""
    # Create the Tkinter root window
    root = tk.Tk()
    
    # Initialize the GUI application
    app = MPCTrajectoryGUI(root)
    
    # Add a welcome message
    app.log_message("MPC Trajectory Designer with Parameter Tuning")
    app.log_message("==================================================")
    app.log_message("This GUI allows you to:")
    app.log_message("1. Create and test custom trajectories")
    app.log_message("2. Modify MPC controller parameters")
    app.log_message("3. Adjust vehicle physical constraints")
    app.log_message("4. Track simulation results")
    app.log_message("\nHow to use:")
    app.log_message("- In the Trajectory tab: Design your path")
    app.log_message("- In the MPC Parameters tab: Tune the controller")
    app.log_message("- In the Vehicle Parameters tab: Set vehicle limits")
    app.log_message("- This Log tab will show simulation results")
    app.log_message("\nReady to start! Select a trajectory or create your own.")
    app.log_message("==================================================")
    
    # Make the window appear on top
    root.lift()           # Bring window to top
    root.attributes('-topmost', True)  # Keep on top
    root.after_idle(root.attributes, '-topmost', False)  # Allow to go behind other windows after
    root.focus_force()  
    
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()