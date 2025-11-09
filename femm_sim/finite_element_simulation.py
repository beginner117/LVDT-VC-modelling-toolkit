import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from simulation import femm_simulation

# Set DPI awareness for high-DPI screens
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # Windows DPI awareness
except Exception as e:
    print(f"DPI awareness setting failed: {e}")

class DynamicSimulationGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Finite Element Simulation of LVDTs and VC actuators")

        # Create the main layout frame for data entry and image in a horizontal bar
        self.main_frame = tk.Frame(self.master)
        self.main_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Placeholder for image on the top right
        self.image_frame = tk.Frame(self.main_frame)
        self.image_frame.grid(row=0, column=1, padx=20, pady=10)

        # Ensure the image frame resizes appropriately
        self.image_frame.grid_propagate(True)
        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

        self.original_images = {}

        # Load and display the default image
        self.image_path = "lvdt2.png"
        self.load_image()

        # Variables to track dynamic inputs
        self.simulation_rows = []
        self.material_inner_var = tk.StringVar()
        self.material_outer_var = tk.StringVar()
        self.material_magnet_var = tk.StringVar()
        self.save_file_var = tk.BooleanVar()
        self.file_name_var = tk.StringVar()

        # Data entry frame next to the image
        self.data_frame = tk.Frame(self.main_frame)
        self.data_frame.grid(row=0, column=0, padx=20, pady=10)

        # Add the initial row
        self.add_simulation_row()

        # Save file option
        self.save_file_checkbox = tk.Checkbutton(self.data_frame, text="Save File", variable=self.save_file_var,
                                                 command=self.toggle_file_name_input)
        self.save_file_checkbox.grid(row=100, column=0, pady=10, sticky="w")  # Set 'sticky="w"' to align it to the left

        # File Name input (initially hidden)
        self.file_name_label = tk.Label(self.data_frame, text="File Name")
        self.file_name_entry = tk.Entry(self.data_frame, textvariable=self.file_name_var)

        # Adjust the grid layout to put 'File Name' right next to the 'Save File' checkbox
        self.file_name_label.grid(row=100, column=1, padx=10, sticky="w")  # Right next to 'Save File'
        self.file_name_entry.grid(row=100, column=2, sticky="w")

        # Initially hide the 'File Name' input
        self.file_name_label.grid_remove()
        self.file_name_entry.grid_remove()

        # Material selection (Optional inputs)
        material_frame = tk.LabelFrame(self.data_frame, text="Material Selection \n(Use the materials only from FEMM material library) ")
        material_frame.grid(row=101, column=0, columnspan=2, pady=10)

        self.inner_label = tk.Label(material_frame, text="Primary Coil Material:\n(def - 32 AWG)")
        self.inner_entry = tk.Entry(material_frame, textvariable=self.material_inner_var)
        self.inner_label.grid(row=0, column=0)
        self.inner_entry.grid(row=0, column=1)

        tk.Label(material_frame, text="Secondary Coil Material:\n(def - 32 AWG)").grid(row=1, column=0)
        tk.Entry(material_frame, textvariable=self.material_outer_var).grid(row=1, column=1)

        tk.Label(material_frame, text="Magnet/Core Material:\n(def - N40)").grid(row=2, column=0)
        tk.Entry(material_frame, textvariable=self.material_magnet_var).grid(row=2, column=1)

        # Optional inputs for execute method next to material selection
        optional_frame = tk.LabelFrame(self.data_frame, text="Execute Parameters")
        optional_frame.grid(row=101, column=1, columnspan=2, pady=10, padx=10)

        self.inn_current_var = tk.DoubleVar()
        self.frequency_var = tk.DoubleVar()
        self.out_current_var = tk.DoubleVar()

        # Primary current (will be hidden for 'VC_only')
        self.primary_current_label = tk.Label(optional_frame, text="Primary current(A):")
        self.primary_current_label.grid(row=0, column=0)
        self.primary_current_entry = tk.Entry(optional_frame, textvariable=self.inn_current_var)
        self.primary_current_entry.grid(row=0, column=1)

        tk.Label(optional_frame, text="Secondary current(A):").grid(row=1, column=0)
        tk.Entry(optional_frame, textvariable=self.out_current_var).grid(row=1, column=1)

        tk.Label(optional_frame, text="Frequency(Hz):").grid(row=2, column=0)
        tk.Entry(optional_frame, textvariable=self.frequency_var).grid(row=2, column=1)

        # Run simulation button
        tk.Button(self.data_frame, text="Run Simulation", command=self.run_simulation).grid(row=102, column=0, columnspan=2, pady=20)

        # Placeholder for simulation output display
        self.output_text = tk.Text(self.master)
        self.output_text.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

        # Footer frame for creator information
        footer_frame = tk.Frame(self.master)
        footer_frame.grid(row=3, column=0, padx=20, pady=5, sticky="e")  # Align it to the right

        # Label with creator name
        creator_label = tk.Label(footer_frame, text="Created by Kumar Akhil", font=("Arial", 12, "italic"), fg="grey")
        creator_label.pack()

    def load_image(self):
        """Loads the image based on the image path"""
        try:
            # Check if original image for current path is cached
            if self.image_path not in self.original_images:
                # Load and store the original image only once
                image = Image.open(self.image_path)
                self.original_images[self.image_path] = image
            else:
                image = self.original_images[self.image_path]
            self.master.update_idletasks()
            frame_width = self.image_frame.winfo_width() or 200; frame_height = self.image_frame.winfo_height() or 200
            # Set a minimum size to avoid downsizing too much
            min_width, min_height = 200, 200
            frame_width = max(frame_width, min_width)
            frame_height = max(frame_height, min_height)
            # Always resize from the original
            resized_image = image.resize((300, 300), Image.LANCZOS)
            self.img = ImageTk.PhotoImage(resized_image)
            if hasattr(self, 'image_label'):
                self.image_label.config(image=self.img)
                self.image_label.image = self.img  # Keep a reference
            else:
                self.image_label = tk.Label(self.image_frame, image=self.img)
                self.image_label.grid(row=0, column=0, padx=10, pady=10)
                self.image_label.image = self.img
        except Exception as e:
            print(f"Error loading image: {e}")

    def update_image_based_on_sensor_type(self, sensor_type, inner_label, inner_entries, outer_entries):
        """Update the image based on the sensor type"""
        if sensor_type == 'LVDT':
            self.image_path = "lvdt2.png"  # LVDT image
        if sensor_type == 'VC':
            self.image_path = "lvdt_vc.png"  # LVDT+VC image
        if sensor_type == 'LVDT_com':
            self.image_path = "lvdt_com.png"  # LVDT commercial image
            inner_label.grid()  # Show the inner coil dimensions
            for entry in inner_entries:
                entry.grid()  # Show inner coil input fields
            for i, entry in enumerate(outer_entries):
                entry.grid()  # Show all 4 outer coil entries
            # Show the Primary Current input
            self.primary_current_label.grid(row=0, column=0)
            self.primary_current_entry.grid(row=0, column=1)
            self.inner_label.grid()
            self.inner_entry.grid()
        elif sensor_type == 'VC_only':
            self.image_path = "lvdt3.png"  # VC_only image
            inner_label.grid_remove()  # Hide the inner coil dimensions
            for entry in inner_entries:
                entry.grid_remove()  # Hide inner coil input fields
            for i, entry in enumerate(outer_entries):
                if i < 3:
                    entry.grid()  # Show only the first 3 entries (height, radius, layers)
                else:
                    entry.grid_remove()  # Hide the 'distance' entry
            # Hide the Primary Current input for VC_only
            self.primary_current_label.grid_remove()
            self.primary_current_entry.grid_remove()
            self.inner_label.grid_remove()
            self.inner_entry.grid_remove()
        self.load_image()
    def toggle_file_name_input(self):
        """Toggle the file name input field visibility based on the Save File checkbox."""
        if self.save_file_var.get():
            self.file_name_label.grid(row=100, column=1)
            self.file_name_entry.grid(row=100, column=2)
        else:
            self.file_name_label.grid_forget()
            self.file_name_entry.grid_forget()

    def add_simulation_row(self):
        row_frame = tk.Frame(self.data_frame)
        row_num = len(self.simulation_rows) + 1
        row_frame.grid(row=row_num, column=0, pady=5, sticky="w")

        # Sensor type (Limited to 3 types)
        sensor_type_var = tk.StringVar()
        sensor_type_label = tk.Label(row_frame, text=f"Sensor Type")
        sensor_type_label.grid(row=0, column=0)
        sensor_type_menu = ttk.Combobox(row_frame, textvariable=sensor_type_var, values=['LVDT', 'VC', 'VC_only', 'LVDT_com'])
        sensor_type_menu.grid(row=0, column=1)

        # Geometry input (inner, outer, magnet dimensions)
        geometry = {}

        # Inner coil dimensions (excluding distance)
        inner_label = tk.Label(row_frame, text="Primary Coil Dimensions (height, radius, no.of layers) in mm ")
        inner_label.grid(row=1, column=0)
        inner_entries = [tk.Entry(row_frame, width=5) for _ in range(3)]  # Only 3 entries now
        for i, entry in enumerate(inner_entries):
            entry.grid(row=1, column=i + 1)
        geometry['inner'] = inner_entries

        # Outer coil dimensions
        outer_label = tk.Label(row_frame, text="Secondary Coil Dimensions (height, radius, no.of layers, distance (btw coil centres)) in mm ")
        outer_label.grid(row=2, column=0)
        outer_entries = [tk.Entry(row_frame, width=5) for _ in range(4)]
        for i, entry in enumerate(outer_entries):
            entry.grid(row=2, column=i + 1)
        geometry['outer'] = outer_entries

        # Magnet dimensions
        magnet_label = tk.Label(row_frame, text="Magnet/Core Dimensions (height, diameter) in mm ")
        magnet_label.grid(row=3, column=0)
        magnet_entries = [tk.Entry(row_frame, width=5) for _ in range(2)]
        for i, entry in enumerate(magnet_entries):
            entry.grid(row=3, column=i + 1)
        geometry['magnet'] = magnet_entries

        # Automatically update the image when sensor type is selected
        sensor_type_menu.bind("<<ComboboxSelected>>",
                              lambda event: self.update_image_based_on_sensor_type(sensor_type_var.get(), inner_label, inner_entries, outer_entries))

        # Coil motion (range and step size)
        motion_label = tk.Label(row_frame, text="Coil relative motion from CENTRE (Range, Step Size) in mm \n [Ex - 5, 1 for 5mm motion with 1mm step]")
        motion_label.grid(row=4, column=0)
        motion_range_entry = tk.Entry(row_frame, width=5)
        motion_range_entry.grid(row=4, column=1)
        step_size_entry = tk.Entry(row_frame, width=5)
        step_size_entry.grid(row=4, column=2)

        #Add everything to the simulation row list
        self.simulation_rows.append({
            'sensor_type': sensor_type_var,
            'geometry': geometry,
            'motion_range': motion_range_entry,
            'step_size': step_size_entry
        })

    def run_simulation(self):
        sensor_types = []
        file_names = []
        geometries = {}
        total_steps = []
        type_or_parameters = []

        # Collect data from all dynamic rows
        for row in self.simulation_rows:
            sensor_types.append(row['sensor_type'].get())
            if row['sensor_type'].get() == 'VC_only':
                geometry = {
                    'outer': [float(entry.get()) for entry in row['geometry']['outer'][:3]],
                    'magnet': [float(entry.get()) for entry in row['geometry']['magnet']],
                }
                # Collect geometry data
            else:
                geometry = {
                    'inner': [float(entry.get()) for entry in row['geometry']['inner']],
                    'outer': [float(entry.get()) for entry in row['geometry']['outer']],
                    'magnet': [float(entry.get()) for entry in row['geometry']['magnet']],
                }
            geometries[row['sensor_type'].get()] = geometry

            # Collect motion data
            total_steps.append({
                'motion_range': row['motion_range'].get(),
                'step_size': row['step_size'].get()
            })

        # Handle file name logic
        if self.save_file_var.get():
            file_name = self.file_name_var.get()
        else:
            file_name = "unsaved" + ".txt"
        file_names.append(file_name)

        # Backend logic for 'out_current'
        sensor_type = sensor_types[0]
        out_current = float(self.out_current_var.get())  # User input as float
        if sensor_type == 'LVDT' or sensor_type == 'VC' or sensor_type == 'LVDT_com':
            out_current = [out_current, out_current]  # Convert to [1, -1] form
        elif sensor_type == 'VC_only':
            out_current = [out_current]  # Single value for VC_only

        # Collect 'inn_current' and 'frequency'
        if sensor_type == 'VC_only':
            inn_current = 0  # Set to 0 by default for VC_only
            materials = [self.material_outer_var.get(), self.material_magnet_var.get()]
        else:
            inn_current = float(self.inn_current_var.get())  # User input for other types
            materials = [self.material_inner_var.get(), self.material_outer_var.get(), self.material_magnet_var.get()]

        frequency = float(self.frequency_var.get())

        # Prepare the simulation instance arguments
        sim_code = femm_simulation.Position_sensor(
            sensor_type=sensor_types,  # sensor type
            sim_range={'steps_size_offset':[[int(float(total_steps[0]['motion_range'])/float(total_steps[0]['step_size'])), float(total_steps[0]['step_size']), 0]]},
            dimensions=geometries[sensor_type],  # coil geometry dimensions
            save=self.save_file_var.get(),
            data={'filename(s)': file_names, 'is default': ['no'], 'design or parameter': 'random'},
            material_prop= materials

        )

        # Execute the simulation
        result = sim_code.execute([inn_current, frequency, out_current])

        # Display output in the text area
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Running simulation with file name: {file_name}\n")
        self.output_text.insert(tk.END, f"Sensor Types: {sensor_types}\n")
        self.output_text.insert(tk.END,
                                f"Primary Current(A): {inn_current}, Frequency(Hz): {frequency}, Secondary Current(A): {out_current}\n")
        #self.output_text.insert(tk.END, "Simulation completed successfully!\n")
        self.output_text.insert(tk.END, f"Simulation Results:\n")
        self.output_text.insert(tk.END, f"Relative coil positions(in mm): {result['coil_positions']}\n")
        if sensor_types[0] == 'LVDT' or sensor_type == 'LVDT_out':
            self.output_text.insert(tk.END, f"Sensitivity(V/mm/A): {result['slope']}\n")
        else:
            self.output_text.insert(tk.END, f"Magnet force(N): {result['magnet_forces']}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicSimulationGUI(root)
    root.mainloop()
























