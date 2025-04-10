"""
GUI for defining custom trajectories for MPC simulation with MPC parameter tuning
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import pathlib
import time
import importlib

# Add the parent directory to the path
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

# Import from the project
from PathPlanning.CubicSpline import cubic_spline_planner
import mpc
from trajectory_config import TRAJECTORIES

class MPCTrajectoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MPC Trajectory Designer with Parameter Tuning")
        self.root.geometry("1400x900")
        
        # Trajectory points
        self.waypoints = []
        self.last_point_marked = False
        
        # MPC Parameters - Default values from the original code
        self.mpc_params = {
            "T": 5,                       # Prediction horizon
            "DT": 0.2,                    # Time step
            "Q1": 1.0,                    # State cost - x position
            "Q2": 1.0,                    # State cost - y position
            "Q3": 0.5,                    # State cost - velocity
            "Q4": 0.5,                    # State cost - yaw
            "R1": 0.01,                   # Input cost - acceleration
            "R2": 0.01,                   # Input cost - steering
            "Rd1": 0.01,                  # Input difference cost - acceleration
            "Rd2": 1.0,                   # Input difference cost - steering
            "MAX_ITER": 3,                # Maximum iterations for MPC
            "MAX_STEER": 45.0,            # Maximum steering angle [deg]
            "MAX_DSTEER": 30.0,           # Maximum steering speed [deg/s]
            "MAX_SPEED": 55.0,            # Maximum speed [km/h]
            "MAX_ACCEL": 1.0,             # Maximum acceleration [m/s²]
            "WB": 2.5                     # Wheelbase [m]
        }
        
        # Create GUI components
        self.create_widgets()
        
        # Default values
        self.dl_var.set("1.0")
        self.speed_var.set("10.0")         # 10.0 / 3.6 m/s (as in the original code)
        self.trajectory_var.set("Circular")
        self.update_trajectory_preview()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a horizontal paned window
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Controls
        control_frame = ttk.Frame(paned_window)
        paned_window.add(control_frame, weight=1)
        
        # Right side: Plots
        plot_frame = ttk.LabelFrame(paned_window, text="Trajectory Preview", padding="10")
        paned_window.add(plot_frame, weight=2)
        
        # Create tabbed interface for controls
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Trajectory Controls
        trajectory_tab = ttk.Frame(notebook, padding="10")
        notebook.add(trajectory_tab, text="Trajectory")
        
        # Tab 2: MPC Parameters
        mpc_params_tab = ttk.Frame(notebook, padding="10")
        notebook.add(mpc_params_tab, text="MPC Parameters")
        
        # Tab 3: Vehicle Parameters
        vehicle_params_tab = ttk.Frame(notebook, padding="10")
        notebook.add(vehicle_params_tab, text="Vehicle Parameters")
        
        # Tab 4: Simulation Log
        log_tab = ttk.Frame(notebook, padding="10")
        notebook.add(log_tab, text="Simulation Log")
        
        # ======== TRAJECTORY TAB =========
        
        # Predefined trajectories selector
        ttk.Label(trajectory_tab, text="Predefined Trajectories:").pack(anchor=tk.W, pady=(0, 5))
        self.trajectory_var = tk.StringVar()
        trajectory_combo = ttk.Combobox(trajectory_tab, textvariable=self.trajectory_var, 
                                        values=list(TRAJECTORIES.keys()), state="readonly")
        trajectory_combo.pack(fill=tk.X, pady=(0, 10))
        trajectory_combo.bind("<<ComboboxSelected>>", lambda e: self.update_trajectory_preview())
        
        # Parameters
        params_frame = ttk.LabelFrame(trajectory_tab, text="Trajectory Generation Parameter", padding="10")
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
        ttk.Label(speed_frame, text="Reference Speed (km/h):").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar()
        ttk.Entry(speed_frame, textvariable=self.speed_var, width=10).pack(side=tk.RIGHT)
        
        preview_frame = ttk.Frame(params_frame)
        preview_frame.pack(fill=tk.X, pady=5)
        ttk.Button(preview_frame, text="Update Preview", command=self.update_trajectory_preview).pack(side=tk.LEFT, padx=2)

        
        # Custom trajectory editor
        custom_frame = ttk.LabelFrame(trajectory_tab, text="Custom Trajectory Editor", padding="10")
        custom_frame.pack(fill=tk.X, expand=False, pady=(0, 10), ipady=5)
        
        ttk.Label(custom_frame, text="Define your own trajectory by multiple clicking on the plot").pack()
        ttk.Label(custom_frame, text="(Plot area is fixed. You can change it in the code if needed.)").pack()
        
        # Buttons for custom trajectory
        buttons_frame = ttk.Frame(custom_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="Clear Points", command=self.clear_points).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Use These Points", command=self.use_custom_points, width =30).pack(side=tk.LEFT, padx=2)

        # Simulation buttons
        sim_frame = ttk.Frame(trajectory_tab)
        sim_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(sim_frame, text="Run Simulation", command=self.run_simulation, 
          height=3, font=("Arial", 14, "bold"), bg="#4CAF50", fg="Black").pack(fill=tk.X, pady=15)        
        # ======== MPC PARAMETERS TAB =========
        
        # Create a canvas with scrollbar for MPC parameters
        canvas_frame = ttk.Frame(mpc_params_tab)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # MPC Parameters - Prediction and Control
        mpc_pred_frame = ttk.LabelFrame(scrollable_frame, text="Prediction and Control", padding=10)
        mpc_pred_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # T - Prediction Horizon
        T_frame = ttk.Frame(mpc_pred_frame)
        T_frame.pack(fill=tk.X, pady=2)
        ttk.Label(T_frame, text="Prediction Horizon (T):").pack(side=tk.LEFT)
        self.T_var = tk.StringVar(value=str(self.mpc_params["T"]))
        ttk.Entry(T_frame, textvariable=self.T_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(T_frame, text="steps").pack(side=tk.RIGHT, padx=(0, 5))
        
        # DT - Time Step
        DT_frame = ttk.Frame(mpc_pred_frame)
        DT_frame.pack(fill=tk.X, pady=2)
        ttk.Label(DT_frame, text="Time Step (DT):").pack(side=tk.LEFT)
        self.DT_var = tk.StringVar(value=str(self.mpc_params["DT"]))
        ttk.Entry(DT_frame, textvariable=self.DT_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(DT_frame, text="seconds").pack(side=tk.RIGHT, padx=(0, 5))
        
        # MAX_ITER - Max iterations
        MAX_ITER_frame = ttk.Frame(mpc_pred_frame)
        MAX_ITER_frame.pack(fill=tk.X, pady=2)
        ttk.Label(MAX_ITER_frame, text="Max Iterations:").pack(side=tk.LEFT)
        self.MAX_ITER_var = tk.StringVar(value=str(self.mpc_params["MAX_ITER"]))
        ttk.Entry(MAX_ITER_frame, textvariable=self.MAX_ITER_var, width=10).pack(side=tk.RIGHT)
        
        # MPC Parameters - Cost Matrices
        cost_frame = ttk.LabelFrame(scrollable_frame, text="Cost Matrices", padding=10)
        cost_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # State cost matrix Q
        ttk.Label(cost_frame, text="State Cost Matrix (Q):", font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Q1 - x position weight
        Q1_frame = ttk.Frame(cost_frame)
        Q1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(Q1_frame, text="Q1 (x position):").pack(side=tk.LEFT)
        self.Q1_var = tk.StringVar(value=str(self.mpc_params["Q1"]))
        ttk.Entry(Q1_frame, textvariable=self.Q1_var, width=10).pack(side=tk.RIGHT)
        
        # Q2 - y position weight
        Q2_frame = ttk.Frame(cost_frame)
        Q2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(Q2_frame, text="Q2 (y position):").pack(side=tk.LEFT)
        self.Q2_var = tk.StringVar(value=str(self.mpc_params["Q2"]))
        ttk.Entry(Q2_frame, textvariable=self.Q2_var, width=10).pack(side=tk.RIGHT)
        
        # Q3 - velocity weight
        Q3_frame = ttk.Frame(cost_frame)
        Q3_frame.pack(fill=tk.X, pady=2)
        ttk.Label(Q3_frame, text="Q3 (velocity):").pack(side=tk.LEFT)
        self.Q3_var = tk.StringVar(value=str(self.mpc_params["Q3"]))
        ttk.Entry(Q3_frame, textvariable=self.Q3_var, width=10).pack(side=tk.RIGHT)
        
        # Q4 - yaw weight
        Q4_frame = ttk.Frame(cost_frame)
        Q4_frame.pack(fill=tk.X, pady=2)
        ttk.Label(Q4_frame, text="Q4 (yaw):").pack(side=tk.LEFT)
        self.Q4_var = tk.StringVar(value=str(self.mpc_params["Q4"]))
        ttk.Entry(Q4_frame, textvariable=self.Q4_var, width=10).pack(side=tk.RIGHT)
        
        # Input cost matrix R
        ttk.Label(cost_frame, text="Input Cost Matrix (R):", font=("", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # R1 - acceleration weight
        R1_frame = ttk.Frame(cost_frame)
        R1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(R1_frame, text="R1 (acceleration):").pack(side=tk.LEFT)
        self.R1_var = tk.StringVar(value=str(self.mpc_params["R1"]))
        ttk.Entry(R1_frame, textvariable=self.R1_var, width=10).pack(side=tk.RIGHT)
        
        # R2 - steering weight
        R2_frame = ttk.Frame(cost_frame)
        R2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(R2_frame, text="R2 (steering):").pack(side=tk.LEFT)
        self.R2_var = tk.StringVar(value=str(self.mpc_params["R2"]))
        ttk.Entry(R2_frame, textvariable=self.R2_var, width=10).pack(side=tk.RIGHT)
        
        # Input difference cost matrix Rd
        ttk.Label(cost_frame, text="Input Difference Cost Matrix (Rd):", font=("", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # Rd1 - acceleration difference weight
        Rd1_frame = ttk.Frame(cost_frame)
        Rd1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(Rd1_frame, text="Rd1 (accel diff):").pack(side=tk.LEFT)
        self.Rd1_var = tk.StringVar(value=str(self.mpc_params["Rd1"]))
        ttk.Entry(Rd1_frame, textvariable=self.Rd1_var, width=10).pack(side=tk.RIGHT)
        
        # Rd2 - steering difference weight
        Rd2_frame = ttk.Frame(cost_frame)
        Rd2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(Rd2_frame, text="Rd2 (steering diff):").pack(side=tk.LEFT)
        self.Rd2_var = tk.StringVar(value=str(self.mpc_params["Rd2"]))
        ttk.Entry(Rd2_frame, textvariable=self.Rd2_var, width=10).pack(side=tk.RIGHT)
        
        # Buttons for MPC parameters
        mpc_buttons_frame = ttk.Frame(scrollable_frame)
        mpc_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(mpc_buttons_frame, text="Reset to Default", command=self.reset_mpc_params).pack(side=tk.LEFT, padx=5)
        ttk.Button(mpc_buttons_frame, text="Apply Parameters", command=self.apply_mpc_params).pack(side=tk.LEFT, padx=5)
        
        # ======== VEHICLE PARAMETERS TAB =========
        
        vehicle_frame = ttk.LabelFrame(vehicle_params_tab, text="Vehicle Constraints", padding=10)
        vehicle_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # MAX_STEER - Maximum steering angle
        MAX_STEER_frame = ttk.Frame(vehicle_frame)
        MAX_STEER_frame.pack(fill=tk.X, pady=2)
        ttk.Label(MAX_STEER_frame, text="Max Steering Angle:").pack(side=tk.LEFT)
        self.MAX_STEER_var = tk.StringVar(value=str(self.mpc_params["MAX_STEER"]))
        ttk.Entry(MAX_STEER_frame, textvariable=self.MAX_STEER_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(MAX_STEER_frame, text="degrees").pack(side=tk.RIGHT, padx=(0, 5))
        
        # MAX_DSTEER - Maximum steering speed
        MAX_DSTEER_frame = ttk.Frame(vehicle_frame)
        MAX_DSTEER_frame.pack(fill=tk.X, pady=2)
        ttk.Label(MAX_DSTEER_frame, text="Max Steering Speed:").pack(side=tk.LEFT)
        self.MAX_DSTEER_var = tk.StringVar(value=str(self.mpc_params["MAX_DSTEER"]))
        ttk.Entry(MAX_DSTEER_frame, textvariable=self.MAX_DSTEER_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(MAX_DSTEER_frame, text="degrees/s").pack(side=tk.RIGHT, padx=(0, 5))
        
        # MAX_SPEED - Maximum speed
        MAX_SPEED_frame = ttk.Frame(vehicle_frame)
        MAX_SPEED_frame.pack(fill=tk.X, pady=2)
        ttk.Label(MAX_SPEED_frame, text="Max Speed:").pack(side=tk.LEFT)
        self.MAX_SPEED_var = tk.StringVar(value=str(self.mpc_params["MAX_SPEED"]))
        ttk.Entry(MAX_SPEED_frame, textvariable=self.MAX_SPEED_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(MAX_SPEED_frame, text="km/h").pack(side=tk.RIGHT, padx=(0, 5))
        
        # MAX_ACCEL - Maximum acceleration
        MAX_ACCEL_frame = ttk.Frame(vehicle_frame)
        MAX_ACCEL_frame.pack(fill=tk.X, pady=2)
        ttk.Label(MAX_ACCEL_frame, text="Max Acceleration:").pack(side=tk.LEFT)
        self.MAX_ACCEL_var = tk.StringVar(value=str(self.mpc_params["MAX_ACCEL"]))
        ttk.Entry(MAX_ACCEL_frame, textvariable=self.MAX_ACCEL_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(MAX_ACCEL_frame, text="m/s²").pack(side=tk.RIGHT, padx=(0, 5))
        
        # Vehicle physical properties
        vehicle_phys_frame = ttk.LabelFrame(vehicle_params_tab, text="Vehicle Physical Properties", padding=10)
        vehicle_phys_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # WB - Wheelbase
        WB_frame = ttk.Frame(vehicle_phys_frame)
        WB_frame.pack(fill=tk.X, pady=2)
        ttk.Label(WB_frame, text="Wheelbase (WB):").pack(side=tk.LEFT)
        self.WB_var = tk.StringVar(value=str(mpc.WB))
        ttk.Entry(WB_frame, textvariable=self.WB_var, width=10).pack(side=tk.RIGHT)
        ttk.Label(WB_frame, text="m").pack(side=tk.RIGHT, padx=(0, 5))
        
        # Apply vehicle parameters button
        vehicle_button_frame = ttk.Frame(vehicle_params_tab)
        vehicle_button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(vehicle_button_frame, text="Apply Vehicle Parameters", 
                  command=self.apply_vehicle_params).pack(side=tk.LEFT, padx=5)
        
        # ======== LOG TAB =========
        
        # Create a text widget for logging
        self.log_text = scrolledtext.ScrolledText(log_tab, wrap=tk.WORD, width=50, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.insert(tk.END, "Simulation log will be displayed here...\n")
        self.log_text.config(state=tk.DISABLED)
        
        # ======== PLOT FRAME =========
        
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
    
    def log_message(self, message):
        """Add message to the log tab"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
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
        
        self.log_message(f"Custom trajectory with {len(self.waypoints)} points set.")
        self.update_trajectory_preview()
    
    def update_plot_with_custom_points(self):
        """Update the plot to show custom points"""
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # Set fixed limits for custom trajectory editor
        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        
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
        
        title = "Trajectory Editor (Fixed -100 to 100 range)"
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
                self.ax.set_xlim(-100, 100)
                self.ax.set_ylim(-100, 100)
            
            self.ax.plot(ax, ay, 'bo', label="Waypoints")
            self.ax.plot(cx, cy, 'r-', label="Spline Trajectory")
            
            self.ax.set_title(f"Trajectory Preview: {selected_trajectory}")
            self.ax.set_xlabel("X [m]")
            self.ax.set_ylabel("Y [m]")
            self.ax.legend()
            self.canvas.draw()
            
            self.log_message(f"Updated trajectory preview: {selected_trajectory}")
            
        except Exception as e:
            self.log_message(f"Error: Failed to generate trajectory: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate trajectory: {str(e)}")
    
    def reset_mpc_params(self):
        """Reset MPC parameters to default values"""
        # Reset to original values
        self.T_var.set(str(5))
        self.DT_var.set(str(0.2))
        self.Q1_var.set(str(1.0))
        self.Q2_var.set(str(1.0))
        self.Q3_var.set(str(0.5))
        self.Q4_var.set(str(0.5))
        self.R1_var.set(str(0.01))
        self.R2_var.set(str(0.01))
        self.Rd1_var.set(str(0.01))
        self.Rd2_var.set(str(1.0))
        self.MAX_ITER_var.set(str(3))
        self.MAX_STEER_var.set(str(45.0))
        self.MAX_DSTEER_var.set(str(30.0))
        self.MAX_SPEED_var.set(str(55.0))
        self.MAX_ACCEL_var.set(str(1.0))
        self.WB_var.set(str(2.5))
        
        self.log_message("MPC parameters reset to default values.")
    
    def apply_mpc_params(self):
        """Apply MPC parameters to the mpc module"""
        try:
            # Update the mpc module parameters
            mpc.T = int(float(self.T_var.get()))
            mpc.DT = float(self.DT_var.get())
            
            # Update Q matrix
            Q1 = float(self.Q1_var.get())
            Q2 = float(self.Q2_var.get())
            Q3 = float(self.Q3_var.get())
            Q4 = float(self.Q4_var.get())
            mpc.Q = np.diag([Q1, Q2, Q3, Q4])
            mpc.Qf = mpc.Q  # Important: Update final state cost matrix
            
            # Update R matrix
            R1 = float(self.R1_var.get())
            R2 = float(self.R2_var.get())
            mpc.R = np.diag([R1, R2])
            
            # Update Rd matrix
            Rd1 = float(self.Rd1_var.get())
            Rd2 = float(self.Rd2_var.get())
            mpc.Rd = np.diag([Rd1, Rd2])
            
            # Update other parameters
            mpc.MAX_ITER = int(float(self.MAX_ITER_var.get()))
            
            # Log updates
            self.log_message("Applied MPC parameters:")
            self.log_message(f"T={mpc.T}, DT={mpc.DT}")
            self.log_message(f"Q=[{Q1}, {Q2}, {Q3}, {Q4}]")
            self.log_message(f"Qf=[{mpc.Qf[0,0]}, {mpc.Qf[1,1]}, {mpc.Qf[2,2]}, {mpc.Qf[3,3]}]")
            self.log_message(f"R=[{R1}, {R2}]")
            self.log_message(f"Rd=[{Rd1}, {Rd2}]")
            self.log_message(f"MAX_ITER={mpc.MAX_ITER}")
            
            messagebox.showinfo("Success", "MPC parameters applied successfully.")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numbers: {str(e)}")
    
    def apply_vehicle_params(self):
        """Apply vehicle parameters to the mpc module"""
        try:
            # Convert degrees to radians for steering angles
            mpc.MAX_STEER = np.deg2rad(float(self.MAX_STEER_var.get()))
            mpc.MAX_DSTEER = np.deg2rad(float(self.MAX_DSTEER_var.get()))
            
            # Convert km/h to m/s for speed
            mpc.MAX_SPEED = float(self.MAX_SPEED_var.get()) / 3.6
            
            # Other parameters
            mpc.MAX_ACCEL = float(self.MAX_ACCEL_var.get())
            mpc.WB = float(self.WB_var.get())
            
            # Log updates
            self.log_message("Applied vehicle parameters:")
            self.log_message(f"MAX_STEER={np.rad2deg(mpc.MAX_STEER)}° ({mpc.MAX_STEER:.4f} rad)")
            self.log_message(f"MAX_DSTEER={np.rad2deg(mpc.MAX_DSTEER)}°/s ({mpc.MAX_DSTEER:.4f} rad/s)")
            self.log_message(f"MAX_SPEED={self.MAX_SPEED_var.get()} km/h ({mpc.MAX_SPEED:.4f} m/s)")
            self.log_message(f"MAX_ACCEL={mpc.MAX_ACCEL} m/s²")
            self.log_message(f"WB={mpc.WB} m")
            
            messagebox.showinfo("Success", "Vehicle parameters applied successfully.")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numbers: {str(e)}")
            
    def run_simulation(self):
        """Run the MPC simulation with the selected trajectory"""
        selected_trajectory = self.trajectory_var.get()
        
        try:
            # Apply the current MPC and vehicle parameters
            self.apply_mpc_params()
            self.apply_vehicle_params()
            
            # Get parameters
            try:
                dl = float(self.dl_var.get())
                target_speed = float(self.speed_var.get()) / 3.6  # Convert km/h to m/s
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please enter valid numbers: {str(e)}")
                return
            
            # Get waypoints function from dictionary
            waypoints_func = TRAJECTORIES[selected_trajectory]
            waypoints = waypoints_func()
            
            # Extract x and y coordinates
            ax = [point[0] for point in waypoints]
            ay = [point[1] for point in waypoints]
            
            # Generate spline curve - directly use the cubic spline planner
            # This matches the approach in the original code
            cx, cy, cyaw, ck, _ = cubic_spline_planner.calc_spline_course(ax, ay, ds=dl)
            
            # Special handling for switch_back trajectory
            if selected_trajectory == "switchback":
                # Apply yaw modification for the second part - like in original code
                midpoint = len(ax) // 2
                for i in range(midpoint, len(cyaw)):
                    cyaw[i] = cyaw[i] - math.pi
            
            # Smooth the yaw angles
            cyaw = mpc.smooth_yaw(cyaw)
            
            # Calculate speed profile
            sp = mpc.calc_speed_profile(cx, cy, cyaw, target_speed)
            
            # Set initial state exactly as in original code
            initial_state = mpc.State(x=cx[0], y=cy[0], yaw=cyaw[0], v=0.0)
            
            # Log current MPC parameters
            self.log_message("\n=== Starting Simulation ===")
            self.log_message(f"Trajectory: {selected_trajectory}")
            self.log_message(f"Target speed: {float(self.speed_var.get())} km/h ({target_speed:.2f} m/s)")
            self.log_message(f"MPC Parameters:")
            self.log_message(f"  T={mpc.T}, DT={mpc.DT}")
            self.log_message(f"  Q=[{mpc.Q[0,0]}, {mpc.Q[1,1]}, {mpc.Q[2,2]}, {mpc.Q[3,3]}]")
            self.log_message(f"  R=[{mpc.R[0,0]}, {mpc.R[1,1]}]")
            self.log_message(f"  Rd=[{mpc.Rd[0,0]}, {mpc.Rd[1,1]}]")
            
            # Show message
            messagebox.showinfo("Simulation", 
                            "Simulation will start in a new window.\n"
                            "Press ESC to stop the simulation.")
            
            # Always show animation for GUI
            original_show_animation = mpc.show_animation
            mpc.show_animation = True
            
            # Run simulation in a separate window
            plt.figure(figsize=(10, 8))
            start_time = time.time()
            t, x, y, yaw, v, d, a = mpc.do_simulation(
                cx, cy, cyaw, ck, sp, dl, initial_state)
            
            elapsed_time = time.time() - start_time
            
            # Log simulation results
            self.log_message(f"Simulation completed in {elapsed_time:.2f} seconds")
            self.log_message(f"Simulation time: {t[-1]:.2f} seconds")
            self.log_message(f"Average speed: {sum(v)/len(v)*3.6:.2f} km/h")
            self.log_message(f"Maximum steering angle: {max(abs(angle) for angle in d):.4f} rad")
            self.log_message("=== Simulation Ended ===\n")
            
            # Restore original setting
            mpc.show_animation = original_show_animation
            
        except Exception as e:
            error_msg = f"Simulation failed: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
            
def main():
    root = tk.Tk()
    app = MPCTrajectoryGUI(root)
    
    # Add a title and introduction
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
    
    root.mainloop()

if __name__ == "__main__":
    main()