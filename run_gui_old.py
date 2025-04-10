"""
GUI for defining custom trajectories for MPC simulation
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import pathlib
import time

# Add the parent directory to the path
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

# Import from the project
from PathPlanning.CubicSpline import cubic_spline_planner
from mpc import (
    State, do_simulation, calc_speed_profile, TARGET_SPEED
)
from trajectory_config import TRAJECTORIES

class MPCTrajectoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MPC Trajectory Designer")
        self.root.geometry("1200x800")
        
        # Trajectory points
        self.waypoints = []
        self.last_point_marked = False
        
        # Create GUI components
        self.create_widgets()
        
        # Default values
        self.dl_var.set("1.0")
        self.speed_var.set(str(TARGET_SPEED))
        self.trajectory_var.set("circular")
        self.update_trajectory_preview()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Predefined trajectories selector
        ttk.Label(control_frame, text="Predefined Trajectories:").pack(anchor=tk.W, pady=(0, 5))
        self.trajectory_var = tk.StringVar()
        trajectory_combo = ttk.Combobox(control_frame, textvariable=self.trajectory_var, 
                                        values=list(TRAJECTORIES.keys()), state="readonly")
        trajectory_combo.pack(fill=tk.X, pady=(0, 10))
        trajectory_combo.bind("<<ComboboxSelected>>", lambda e: self.update_trajectory_preview())
        
        # Parameters
        params_frame = ttk.LabelFrame(control_frame, text="Simulation Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # DL parameter
        dl_frame = ttk.Frame(params_frame)
        dl_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dl_frame, text="Points Distance (dl):").pack(side=tk.LEFT)
        self.dl_var = tk.StringVar()
        ttk.Entry(dl_frame, textvariable=self.dl_var, width=10).pack(side=tk.RIGHT)
        
        # Speed parameter
        speed_frame = ttk.Frame(params_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Target Speed (m/s):").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar()
        ttk.Entry(speed_frame, textvariable=self.speed_var, width=10).pack(side=tk.RIGHT)
        
        # Custom trajectory editor
        custom_frame = ttk.LabelFrame(control_frame, text="Custom Trajectory Editor", padding="10")
        custom_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(custom_frame, text="Define your own trajectory by clicking on the plot").pack()
        ttk.Label(custom_frame, text="(Plot area is fixed to -50 to 50 range)").pack()
        
        # Buttons for custom trajectory
        buttons_frame = ttk.Frame(custom_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="Clear Points", command=self.clear_points).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Mark as Last Point", command=self.mark_last_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Use Custom Points", command=self.use_custom_points).pack(side=tk.LEFT, padx=2)
        
        # Simulation buttons
        sim_frame = ttk.Frame(control_frame)
        sim_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(sim_frame, text="Update Preview", command=self.update_trajectory_preview).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(sim_frame, text="Run Simulation", command=self.run_simulation).pack(fill=tk.X)
        
        # Right side: Plots
        plot_frame = ttk.LabelFrame(main_frame, text="Trajectory Preview", padding="10")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X [m]")
        self.ax.set_ylabel("Y [m]")
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # Add the figure to the tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect mouse click event
        self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def on_click(self, event):
        """Handle click event on the plot to add points for custom trajectory"""
        if event.inaxes == self.ax and not self.last_point_marked:
            # Only add points if we haven't marked a last point
            self.waypoints.append((event.xdata, event.ydata))
            self.update_plot_with_custom_points()
    
    def clear_points(self):
        """Clear all custom points"""
        self.waypoints = []
        self.last_point_marked = False
        self.update_plot_with_custom_points()
    
    def mark_last_point(self):
        """Mark the most recently added point as the last point in the trajectory"""
        if not self.waypoints:
            messagebox.showwarning("Warning", "No points to mark. Please add points first.")
            return
            
        self.last_point_marked = True
        messagebox.showinfo("Success", f"Point {len(self.waypoints)-1} marked as the last point.\nNo more points will be added after this.")
        self.update_plot_with_custom_points()
    
    def use_custom_points(self):
        """Switch to using custom points for simulation"""
        if len(self.waypoints) < 3:
            messagebox.showwarning("Warning", "Please add at least 3 points for a valid trajectory.")
            return
        
        # Set the trajectories combobox to "custom"
        self.trajectory_var.set("custom")
        
        # Update TRAJECTORIES dictionary's "custom" entry with a new function
        waypoints = self.waypoints.copy()
        TRAJECTORIES["custom"] = lambda: waypoints
        
        self.update_trajectory_preview()
    
    def update_plot_with_custom_points(self):
        """Update the plot to show custom points"""
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # Set fixed limits for custom trajectory editor
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        
        # Plot waypoints
        if self.waypoints:
            x_points = [p[0] for p in self.waypoints]
            y_points = [p[1] for p in self.waypoints]
            self.ax.plot(x_points, y_points, 'bo-', label="Custom Waypoints")
            
            # Annotate points with their index
            for i, (x, y) in enumerate(self.waypoints):
                # If this is the last point and marked as last, highlight it
                if self.last_point_marked and i == len(self.waypoints) - 1:
                    self.ax.plot(x, y, 'ro', markersize=10, label="Last Point")
                    self.ax.annotate(f"{i} (Last)", (x, y), textcoords="offset points", 
                                   xytext=(0, 10), ha='center', color='red', fontweight='bold')
                else:
                    self.ax.annotate(str(i), (x, y), textcoords="offset points", 
                                   xytext=(0, 10), ha='center')
        
        title = "Trajectory Editor (Fixed -50 to 50 range)"
        if self.last_point_marked:
            title += " - Last point marked"
        else:
            title += " - Click to add points"
            
        self.ax.set_title(title)
        self.ax.set_xlabel("X [m]")
        self.ax.set_ylabel("Y [m]")
        self.ax.legend()
        self.canvas.draw()
    
    def update_trajectory_preview(self):
        """Update the preview plot with the selected trajectory"""
        selected_trajectory = self.trajectory_var.get()
        
        try:
            # Get waypoints function from dictionary
            waypoints_func = TRAJECTORIES[selected_trajectory]
            waypoints = waypoints_func()
            
            # Extract x and y coordinates
            ax = [point[0] for point in waypoints]
            ay = [point[1] for point in waypoints]
            
            # Get dl parameter
            try:
                dl = float(self.dl_var.get())
            except ValueError:
                dl = 1.0
                self.dl_var.set("1.0")
            
            # Generate spline curve
            cx, cy, cyaw, ck, _ = cubic_spline_planner.calc_spline_course(ax, ay, ds=dl)
            
            # Update plot
            self.ax.clear()
            self.ax.grid(True)
            self.ax.set_aspect('equal')
            
            # If we're viewing "custom" trajectory, use fixed limits
            if selected_trajectory == "custom":
                self.ax.set_xlim(-50, 50)
                self.ax.set_ylim(-50, 50)
            
            self.ax.plot(ax, ay, 'bo', label="Waypoints")
            self.ax.plot(cx, cy, 'r-', label="Spline Trajectory")
            
            self.ax.set_title(f"Trajectory Preview: {selected_trajectory}")
            self.ax.set_xlabel("X [m]")
            self.ax.set_ylabel("Y [m]")
            self.ax.legend()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate trajectory: {str(e)}")
    
    def run_simulation(self):
        """Run the MPC simulation with the selected trajectory"""
        selected_trajectory = self.trajectory_var.get()
        
        try:
            # Get parameters
            try:
                dl = float(self.dl_var.get())
                target_speed = float(self.speed_var.get())
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please enter valid numbers: {str(e)}")
                return
            
            # Get waypoints function from dictionary
            waypoints_func = TRAJECTORIES[selected_trajectory]
            waypoints = waypoints_func()
            
            # Extract x and y coordinates
            ax = [point[0] for point in waypoints]
            ay = [point[1] for point in waypoints]
            
            # Generate spline curve
            cx, cy, cyaw, ck, _ = cubic_spline_planner.calc_spline_course(ax, ay, ds=dl)
            
            # Calculate speed profile
            sp = calc_speed_profile(cx, cy, cyaw, target_speed)
            
            # Set initial state
            initial_state = State(x=cx[0], y=cy[0], yaw=cyaw[0], v=0.0)
            
            # Show message
            messagebox.showinfo("Simulation", 
                               "Simulation will start in a new window.\n"
                               "Press ESC to stop the simulation.")
            
            # Run simulation (this will show matplotlib animation)
            from mpc import show_animation
            
            # Always show animation for GUI
            original_show_animation = show_animation
            import mpc as mpc_module
            mpc_module.show_animation = True
            
            # Run simulation in a separate window
            plt.figure(figsize=(10, 8))
            t, x, y, yaw, v, d, a = do_simulation(
                cx, cy, cyaw, ck, sp, dl, initial_state)
            
            # Restore original setting
            mpc_module.show_animation = original_show_animation
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")

def main():
    root = tk.Tk()
    app = MPCTrajectoryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()