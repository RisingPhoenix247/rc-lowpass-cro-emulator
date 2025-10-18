import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json

class Component:
    """Electronic component"""
    def __init__(self, comp_type, comp_id, value, unit=""):
        self.type = comp_type
        self.id = comp_id
        self.value = value
        self.unit = unit
        
    def to_dict(self):
        return {
            "type": self.type,
            "id": self.id,
            "value": self.value,
            "unit": self.unit
        }
    
    @staticmethod
    def from_dict(data):
        return Component(data["type"], data["id"], data["value"], data.get("unit", ""))

class RCLowPassCircuit:
    """RC Low-Pass Filter Circuit"""
    def __init__(self, name="RC Low-Pass Filter"):
        self.name = name
        self.components = []
        self.probe_points = {}
        self.description = ""
        
    def add_component(self, component):
        self.components.append(component)
        
    def remove_component(self, comp_id):
        self.components = [c for c in self.components if c.id != comp_id]
        
    def add_probe_point(self, name, signal_key):
        self.probe_points[name] = signal_key
        
    def get_resistor_value(self):
        """Get resistor value from components"""
        for comp in self.components:
            if comp.type == "resistor":
                try:
                    return float(comp.value)
                except:
                    return 1000  # Default
        return 1000
    
    def get_capacitor_value(self):
        """Get capacitor value from components"""
        for comp in self.components:
            if comp.type == "capacitor":
                try:
                    return float(comp.value)
                except:
                    return 100e-9  # Default
        return 100e-9
    
    def calculate_cutoff_frequency(self):
        """Calculate cutoff frequency fc = 1/(2πRC)"""
        R = self.get_resistor_value()
        C = self.get_capacitor_value()
        fc = 1 / (2 * np.pi * R * C)
        return fc
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "components": [c.to_dict() for c in self.components],
            "probe_points": self.probe_points
        }
    
    @staticmethod
    def from_dict(data):
        circuit = RCLowPassCircuit(data.get("name", "RC Low-Pass Filter"))
        circuit.description = data.get("description", "")
        circuit.components = [Component.from_dict(c) for c in data.get("components", [])]
        circuit.probe_points = data.get("probe_points", {})
        return circuit
    
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load_from_file(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return RCLowPassCircuit.from_dict(data)

class RCLowPassSimulator:
    """Simulates RC Low-Pass Filter"""
    
    def generate_square_wave(self, t, freq, amplitude=5.0):
        """Generate square wave signal"""
        return amplitude * np.sign(np.sin(2 * np.pi * freq * t))
    
    def simulate(self, circuit, t, freq):
        """
        Simulate RC Low-Pass Filter
        
        LOW-PASS FILTER:
        - Input -> Resistor -> Output (taken across Capacitor)
        - Capacitor charges/discharges through resistor
        - Fast changes (high freq) -> Capacitor can't keep up -> Blocked
        - Slow changes (low freq) -> Capacitor follows -> Passes
        """
        R = circuit.get_resistor_value()
        C = circuit.get_capacitor_value()
        tau = R * C  # Time constant
        
        # Generate square wave input
        input_signal = self.generate_square_wave(t, freq, amplitude=5.0)
        
        # Simulate capacitor voltage (output)
        output_signal = np.zeros_like(t)
        v_cap = 0  # Initial capacitor voltage
        dt = t[1] - t[0] if len(t) > 1 else 0.0001
        
        for i in range(len(t)):
            # Exponential charging: V_cap approaches V_in with time constant τ
            v_cap += (input_signal[i] - v_cap) * (dt / tau)
            output_signal[i] = v_cap
        
        # Voltage across resistor (input - output)
        resistor_signal = input_signal - output_signal
        
        return {
            "input": input_signal,
            "output": output_signal,
            "resistor": resistor_signal,
            "capacitor": output_signal
        }

class CROEmulator:
    """CRO Emulator for RC Low-Pass Filter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RC Low-Pass Filter Builder & CRO Emulator")
        self.root.geometry("1600x900")
        self.root.configure(bg='#2b2b2b')
        
        self.circuit = RCLowPassCircuit()
        self.simulator = RCLowPassSimulator()
        
        # Oscilloscope parameters
        self.time_div = 1.0
        self.volt_div = 2.0
        self.frequency = 1000
        self.trigger_level = 0.0
        self.is_running = True
        
        # Probing
        self.probe_ch1 = "input"
        self.probe_ch2 = "output"
        self.show_ch1 = True
        self.show_ch2 = True
        
        self.setup_ui()
        self.create_default_circuit()
        self.update_display()
    
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Circuit", command=self.new_circuit)
        file_menu.add_command(label="Save Circuit", command=self.save_circuit)
        file_menu.add_command(label="Load Circuit", command=self.load_circuit)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Build", command=self.show_help)
        help_menu.add_command(label="About RC Low-Pass", command=self.show_about)
        
        # Top toolbar
        toolbar = tk.Frame(self.root, bg='#1a1a1a', height=60)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Label(toolbar, text="🔽 RC LOW-PASS FILTER 🔽", 
                font=('Arial', 14, 'bold'),
                bg='#1a1a1a', fg='#00ff00').pack(side=tk.LEFT, padx=20)
        
        self.circuit_name_label = tk.Label(toolbar, text=self.circuit.name, 
                                          font=('Arial', 12, 'bold'),
                                          bg='#1a1a1a', fg='#ffff00')
        self.circuit_name_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(toolbar, text="📝 Rename", command=self.edit_circuit_name,
                 bg='#3b3b3b', fg='white', font=('Arial', 9, 'bold'),
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        self.cutoff_label = tk.Label(toolbar, text="Cutoff: Calculating...", 
                                     font=('Arial', 11, 'bold'),
                                     bg='#ff6600', fg='white', padx=15, pady=5)
        self.cutoff_label.pack(side=tk.RIGHT, padx=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left: Circuit Builder (narrower)
        builder_frame = tk.Frame(main_frame, bg='#1a1a1a', relief=tk.RIDGE, 
                                borderwidth=3, width=380)
        builder_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        builder_frame.pack_propagate(False)
        
        tk.Label(builder_frame, text="⚡ CIRCUIT BUILDER", 
                font=('Arial', 12, 'bold'),
                bg='#1a1a1a', fg='#00ff00').pack(pady=10)
        
        # Add components section
        add_frame = tk.LabelFrame(builder_frame, text="Add Components", 
                                 bg='#2b2b2b', fg='#ffaa00', 
                                 font=('Arial', 10, 'bold'))
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(add_frame, text="📦 Add Resistor", 
                 command=lambda: self.add_component_dialog("resistor"),
                 bg='#3b3b3b', fg='white', font=('Arial', 9, 'bold'),
                 width=22, pady=8).pack(padx=5, pady=3)
        
        tk.Button(add_frame, text="⚡ Add Capacitor", 
                 command=lambda: self.add_component_dialog("capacitor"),
                 bg='#3b3b3b', fg='white', font=('Arial', 9, 'bold'),
                 width=22, pady=8).pack(padx=5, pady=3)
        
        tk.Button(add_frame, text="🔌 Add Voltage Source", 
                 command=lambda: self.add_component_dialog("source"),
                 bg='#3b3b3b', fg='white', font=('Arial', 9, 'bold'),
                 width=22, pady=8).pack(padx=5, pady=3)
        
        # Components list
        list_frame = tk.LabelFrame(builder_frame, text="Circuit Components", 
                                  bg='#2b2b2b', fg='#ffaa00', 
                                  font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scroll_frame = tk.Frame(list_frame, bg='#2b2b2b')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.component_listbox = tk.Listbox(scroll_frame, 
                                           yscrollcommand=scrollbar.set,
                                           bg='#0a0a0a', fg='#00ff00',
                                           font=('Courier', 10),
                                           selectmode=tk.SINGLE)
        self.component_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.component_listbox.yview)
        
        comp_ctrl_frame = tk.Frame(list_frame, bg='#2b2b2b')
        comp_ctrl_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(comp_ctrl_frame, text="❌ Remove", 
                 command=self.remove_selected_component,
                 bg='#ff4444', fg='white', font=('Arial', 9, 'bold'),
                 width=15).pack(side=tk.LEFT, padx=2)
        
        tk.Button(comp_ctrl_frame, text="🔄 Clear All", 
                 command=self.clear_all_components,
                 bg='#ff8844', fg='white', font=('Arial', 9, 'bold'),
                 width=15).pack(side=tk.LEFT, padx=2)
        
        # Probe points
        probe_config_frame = tk.LabelFrame(builder_frame, text="Probe Points", 
                                          bg='#2b2b2b', fg='#ffaa00', 
                                          font=('Arial', 10, 'bold'))
        probe_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(probe_config_frame, text="⚡ Add Probe Point", 
                 command=self.add_probe_point_dialog,
                 bg='#4444ff', fg='white', font=('Arial', 9, 'bold'),
                 width=20, pady=5).pack(padx=5, pady=5)
        
        self.probe_list_text = tk.Text(probe_config_frame, height=3, 
                                      bg='#0a0a0a', fg='#00ffff',
                                      font=('Courier', 9))
        self.probe_list_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Description
        desc_frame = tk.LabelFrame(builder_frame, text="Description", 
                                  bg='#2b2b2b', fg='#ffaa00', 
                                  font=('Arial', 10, 'bold'))
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.desc_text = tk.Text(desc_frame, height=3, bg='#0a0a0a', fg='#ffffff',
                                font=('Arial', 9), wrap=tk.WORD)
        self.desc_text.pack(fill=tk.X, padx=5, pady=5)
        self.desc_text.bind('<KeyRelease>', self.update_description)
        
        # Center: Oscilloscope
        scope_frame = tk.Frame(main_frame, bg='#1a1a1a', relief=tk.RIDGE, borderwidth=3)
        scope_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(scope_frame, text="📊 OSCILLOSCOPE", 
                font=('Arial', 13, 'bold'),
                bg='#1a1a1a', fg='#00ff00').pack(pady=10)
        
        # Info label
        info_frame = tk.Frame(scope_frame, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.freq_info_label = tk.Label(info_frame, 
                                        text="Frequency: 1000 Hz", 
                                        font=('Arial', 10, 'bold'),
                                        bg='#0066ff', fg='white', pady=5)
        self.freq_info_label.pack(fill=tk.X)
        
        # CRO display
        self.fig = Figure(figsize=(8, 6), facecolor='#0a0a0a')
        self.ax = self.fig.add_subplot(111, facecolor='#0a0a0a')
        
        self.ax.spines['bottom'].set_color('#00ff00')
        self.ax.spines['top'].set_color('#00ff00')
        self.ax.spines['left'].set_color('#00ff00')
        self.ax.spines['right'].set_color('#00ff00')
        self.ax.tick_params(colors='#00ff00', which='both')
        self.ax.grid(True, color='#003300', linestyle='-', linewidth=0.5)
        
        self.line_ch1, = self.ax.plot([], [], color='#ffff00', linewidth=2.5, 
                                      label='CH1', antialiased=True)
        self.line_ch2, = self.ax.plot([], [], color='#00ffff', linewidth=2.5, 
                                      label='CH2', antialiased=True)
        self.trigger_line = self.ax.axhline(y=0, color='#ffaa00', 
                                           linestyle='--', linewidth=1, alpha=0.7)
        
        self.canvas = FigureCanvasTkAgg(self.fig, scope_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right: Controls
        control_frame = tk.Frame(main_frame, bg='#2b2b2b', width=280)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        control_frame.pack_propagate(False)
        
        tk.Label(control_frame, text="CRO CONTROLS", 
                font=('Arial', 11, 'bold'),
                bg='#2b2b2b', fg='#00ff00').pack(pady=(0, 10))
        
        # Channel 1
        ch1_frame = tk.LabelFrame(control_frame, text="CH1 (Yellow)", 
                                 bg='#2b2b2b', fg='#ffff00', font=('Arial', 10, 'bold'))
        ch1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ch1_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ch1_frame, text="Enable", variable=self.ch1_var,
                      bg='#2b2b2b', fg='#ffffff', selectcolor='#1a1a1a',
                      command=self.toggle_channel, font=('Arial', 9)).pack(anchor=tk.W, padx=5, pady=3)
        
        tk.Label(ch1_frame, text="Probe:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 9)).pack(anchor=tk.W, padx=5)
        
        self.ch1_combo = ttk.Combobox(ch1_frame, state='readonly', width=18, font=('Arial', 9))
        self.ch1_combo.bind('<<ComboboxSelected>>', self.change_probe)
        self.ch1_combo.pack(padx=5, pady=3)
        
        # Channel 2
        ch2_frame = tk.LabelFrame(control_frame, text="CH2 (Cyan)", 
                                 bg='#2b2b2b', fg='#00ffff', font=('Arial', 10, 'bold'))
        ch2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ch2_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ch2_frame, text="Enable", variable=self.ch2_var,
                      bg='#2b2b2b', fg='#ffffff', selectcolor='#1a1a1a',
                      command=self.toggle_channel, font=('Arial', 9)).pack(anchor=tk.W, padx=5, pady=3)
        
        tk.Label(ch2_frame, text="Probe:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 9)).pack(anchor=tk.W, padx=5)
        
        self.ch2_combo = ttk.Combobox(ch2_frame, state='readonly', width=18, font=('Arial', 9))
        self.ch2_combo.bind('<<ComboboxSelected>>', self.change_probe)
        self.ch2_combo.pack(padx=5, pady=3)
        
        # Frequency - MOST IMPORTANT
        self.create_section(control_frame, "⚡ FREQUENCY")
        tk.Label(control_frame, text="Adjust to see filter response!", 
                bg='#2b2b2b', fg='#ff6600', font=('Arial', 8, 'bold')).pack()
        
        self.freq_scale = self.create_slider(control_frame, "Hz:", 
                                             100, 10000, self.frequency,
                                             self.update_frequency, resolution=100)
        
        # Timebase
        self.create_section(control_frame, "TIMEBASE")
        self.time_scale = self.create_slider(control_frame, "Time/Div (ms):", 
                                             0.1, 10, self.time_div,
                                             self.update_time_div, resolution=0.1)
        
        # Vertical
        self.create_section(control_frame, "VERTICAL")
        self.volt_scale = self.create_slider(control_frame, "Volt/Div (V):", 
                                             0.5, 10, self.volt_div,
                                             self.update_volt_div, resolution=0.5)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='#2b2b2b')
        button_frame.pack(pady=15)
        
        self.run_button = tk.Button(button_frame, text="STOP", 
                                    command=self.toggle_run,
                                    bg='#ff4444', fg='white', 
                                    font=('Arial', 10, 'bold'),
                                    width=12, height=2)
        self.run_button.pack(pady=5)
    
    def create_section(self, parent, title):
        label = tk.Label(parent, text=title, font=('Arial', 9, 'bold'),
                        bg='#2b2b2b', fg='#00dd00')
        label.pack(pady=(10, 2))
        
    def create_slider(self, parent, label_text, from_, to, initial, command, 
                     resolution=1):
        frame = tk.Frame(parent, bg='#2b2b2b')
        frame.pack(pady=2, padx=10, fill=tk.X)
        
        label = tk.Label(frame, text=label_text, bg='#2b2b2b', 
                        fg='#ffffff', font=('Arial', 8))
        label.pack(anchor=tk.W)
        
        scale = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL,
                        command=command, bg='#3b3b3b', fg='#00ff00',
                        troughcolor='#1a1a1a', highlightthickness=0,
                        resolution=resolution, length=240)
        scale.set(initial)
        scale.pack(fill=tk.X)
        
        return scale
    
    def create_default_circuit(self):
        """Create a default RC low-pass filter"""
        self.circuit.add_component(Component("source", "V1", "5", "V"))
        self.circuit.add_component(Component("resistor", "R1", "1000", "Ω"))
        self.circuit.add_component(Component("capacitor", "C1", "100e-9", "F"))
        
        self.circuit.add_probe_point("Input Signal", "input")
        self.circuit.add_probe_point("Filtered Output", "output")
        self.circuit.add_probe_point("Voltage across R1", "resistor")
        
        self.circuit.description = "RC Low-Pass Filter: Smooths square waves by blocking high frequencies. Cutoff frequency fc = 1/(2πRC) ≈ 1591 Hz"
        
        self.update_component_list()
        self.update_probe_list()
        self.update_probe_combos()
        self.desc_text.insert('1.0', self.circuit.description)
        self.update_cutoff_display()
    
    def add_component_dialog(self, comp_type):
        """Dialog to add component"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add {comp_type.title()}")
        dialog.geometry("400x280")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"ADD {comp_type.upper()}", 
                font=('Arial', 14, 'bold'),
                bg='#2b2b2b', fg='#00ff00').pack(pady=15)
        
        # Component ID
        id_frame = tk.Frame(dialog, bg='#2b2b2b')
        id_frame.pack(pady=8)
        tk.Label(id_frame, text="Component ID:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=5)
        id_entry = tk.Entry(id_frame, font=('Arial', 11), width=18)
        id_entry.pack(side=tk.LEFT, padx=5)
        id_entry.insert(0, f"{comp_type[0].upper()}{len(self.circuit.components)+1}")
        
        # Value
        val_frame = tk.Frame(dialog, bg='#2b2b2b')
        val_frame.pack(pady=8)
        tk.Label(val_frame, text="Value:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=5)
        val_entry = tk.Entry(val_frame, font=('Arial', 11), width=18)
        val_entry.pack(side=tk.LEFT, padx=5)
        
        # Unit
        unit_frame = tk.Frame(dialog, bg='#2b2b2b')
        unit_frame.pack(pady=8)
        tk.Label(unit_frame, text="Unit:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=5)
        unit_entry = tk.Entry(unit_frame, font=('Arial', 11), width=18)
        unit_entry.pack(side=tk.LEFT, padx=5)
        
        # Defaults
        defaults = {
            "source": ("5", "V"),
            "resistor": ("1000", "Ω"),
            "capacitor": ("100e-9", "F")
        }
        
        if comp_type in defaults:
            val_entry.insert(0, defaults[comp_type][0])
            unit_entry.insert(0, defaults[comp_type][1])
        
        # Help
        help_texts = {
            "resistor": "Examples:\n1000 = 1kΩ\n10000 = 10kΩ\n100000 = 100kΩ",
            "capacitor": "Examples:\n100e-9 = 100nF\n1e-6 = 1µF\n10e-6 = 10µF",
            "source": "Voltage amplitude in Volts\nExample: 5 = 5V square wave"
        }
        
        tk.Label(dialog, text=help_texts.get(comp_type, ""), 
                bg='#2b2b2b', fg='#ffaa00', font=('Arial', 9),
                justify=tk.LEFT).pack(pady=10)
        
        def add_component():
            comp_id = id_entry.get().strip()
            value = val_entry.get().strip()
            unit = unit_entry.get().strip()
            
            if not comp_id or not value:
                messagebox.showerror("Error", "Please fill in all required fields!")
                return
            
            self.circuit.add_component(Component(comp_type, comp_id, value, unit))
            self.update_component_list()
            self.update_cutoff_display()
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg='#2b2b2b')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✓ Add", command=add_component,
                 bg='#44ff44', fg='black', font=('Arial', 10, 'bold'),
                 width=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Cancel", command=dialog.destroy,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'),
                 width=10, pady=5).pack(side=tk.LEFT, padx=5)
    
    def add_probe_point_dialog(self):
        """Dialog to add probe point"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Probe Point")
        dialog.geometry("400x250")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="ADD PROBE POINT", 
                font=('Arial', 14, 'bold'),
                bg='#2b2b2b', fg='#00ff00').pack(pady=15)
        
        # Probe name
        name_frame = tk.Frame(dialog, bg='#2b2b2b')
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Probe Name:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=5)
        name_entry = tk.Entry(name_frame, font=('Arial', 11), width=20)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        # Signal key
        key_frame = tk.Frame(dialog, bg='#2b2b2b')
        key_frame.pack(pady=10)
        tk.Label(key_frame, text="Signal Key:", bg='#2b2b2b', 
                fg='#ffffff', font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=5)
        key_combo = ttk.Combobox(key_frame, font=('Arial', 11), width=18)
        key_combo['values'] = ["input", "output", "resistor", "capacitor"]
        key_combo.set("output")
        key_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(dialog, text="Available signals:\ninput, output, resistor, capacitor", 
                bg='#2b2b2b', fg='#ffaa00', font=('Arial', 9),
                justify=tk.LEFT).pack(pady=10)
        
        def add_probe():
            name = name_entry.get().strip()
            key = key_combo.get().strip()
            
            if not name or not key:
                messagebox.showerror("Error", "Please fill in all fields!")
                return
            
            self.circuit.add_probe_point(name, key)
            self.update_probe_list()
            self.update_probe_combos()
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg='#2b2b2b')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✓ Add", command=add_probe,
                 bg='#44ff44', fg='black', font=('Arial', 10, 'bold'),
                 width=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Cancel", command=dialog.destroy,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'),
                 width=10, pady=5).pack(side=tk.LEFT, padx=5)
    
    def remove_selected_component(self):
        selection = self.component_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a component to remove!")
            return
        
        idx = selection[0]
        if idx < len(self.circuit.components):
            comp = self.circuit.components[idx]
            if messagebox.askyesno("Confirm", f"Remove {comp.id}?"):
                self.circuit.remove_component(comp.id)
                self.update_component_list()
                self.update_cutoff_display()
    
    def clear_all_components(self):
        if messagebox.askyesno("Confirm", "Clear all components?"):
            self.circuit.components = []
            self.update_component_list()
            self.update_cutoff_display()
    
    def update_component_list(self):
        self.component_listbox.delete(0, tk.END)
        for comp in self.circuit.components:
            display = f"{comp.id}: {comp.type.upper()} = {comp.value}"
            if comp.unit:
                display += f" {comp.unit}"
            self.component_listbox.insert(tk.END, display)
    
    def update_probe_list(self):
        self.probe_list_text.delete('1.0', tk.END)
        for name, key in self.circuit.probe_points.items():
            self.probe_list_text.insert(tk.END, f"{name} → {key}\n")
    
    def update_probe_combos(self):
        probe_names = list(self.circuit.probe_points.keys())
        if not probe_names:
            probe_names = ["input", "output"]
        
        self.ch1_combo['values'] = probe_names
        self.ch2_combo['values'] = probe_names
        
        if probe_names:
            if self.ch1_combo.get() not in probe_names:
                self.ch1_combo.set(probe_names[0])
            if self.ch2_combo.get() not in probe_names:
                self.ch2_combo.set(probe_names[-1] if len(probe_names) > 1 else probe_names[0])
    
    def update_cutoff_display(self):
        """Update cutoff frequency display"""
        fc = self.circuit.calculate_cutoff_frequency()
        self.cutoff_label.config(text=f"Cutoff: {fc:.1f} Hz")
    
    def update_description(self, event=None):
        self.circuit.description = self.desc_text.get('1.0', tk.END).strip()
    
    def edit_circuit_name(self):
        name = simpledialog.askstring("Circuit Name", "Enter circuit name:",
                                     initialvalue=self.circuit.name)
        if name:
            self.circuit.name = name
            self.circuit_name_label.config(text=name)
    
    def new_circuit(self):
        if messagebox.askyesno("New Circuit", "Clear and create new circuit?"):
            self.circuit = RCLowPassCircuit()
            self.create_default_circuit()
    
    def save_circuit(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.circuit.save_to_file(filename)
                messagebox.showinfo("Success", f"Circuit saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
    
    def load_circuit(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.circuit = RCLowPassCircuit.load_from_file(filename)
                self.update_component_list()
                self.update_probe_list()
                self.update_probe_combos()
                self.desc_text.delete('1.0', tk.END)
                self.desc_text.insert('1.0', self.circuit.description)
                self.circuit_name_label.config(text=self.circuit.name)
                self.update_cutoff_display()
                messagebox.showinfo("Success", f"Circuit loaded from:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load:\n{str(e)}")
    
    def show_help(self):
        help_text = """HOW TO BUILD RC LOW-PASS FILTER:

1. ADD COMPONENTS:
   • Voltage Source: Input signal (5V square wave)
   • Resistor: Use 1000 for 1kΩ
   • Capacitor: Use 100e-9 for 100nF

2. CUTOFF FREQUENCY:
   fc = 1/(2πRC)
   Example: R=1kΩ, C=100nF → fc≈1591Hz

3. PROBE POINTS:
   • "input" - Input square wave
   • "output" - Filtered output (across capacitor)
   • "resistor" - Voltage across resistor

4. SAVE/LOAD:
   • File → Save Circuit (as .json)
   • File → Load Circuit (open .json)

5. TEST YOUR FILTER:
   • Set freq BELOW cutoff → Signal passes
   • Set freq ABOVE cutoff → Signal blocked
   • Watch the output get smoother!

TIP: Try different R and C values to change cutoff frequency!"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Help")
        dialog.geometry("550x450")
        dialog.configure(bg='#2b2b2b')
        
        text = tk.Text(dialog, wrap=tk.WORD, bg='#0a0a0a', fg='#00ff00',
                      font=('Courier', 10), padx=15, pady=15)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', help_text)
        text.config(state=tk.DISABLED)
        
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg='#4444ff', fg='white', font=('Arial', 10, 'bold'),
                 width=15, pady=5).pack(pady=10)
    
    def show_about(self):
        about_text = """RC LOW-PASS FILTER

WHAT IT DOES:
• Passes LOW frequencies
• Blocks HIGH frequencies
• Smooths sharp edges of square waves

HOW IT WORKS:
Input → Resistor → Output (across Capacitor)
                    ↓
                   GND

The capacitor takes time to charge/discharge:
• FAST changes (high freq) → Can't keep up → BLOCKED
• SLOW changes (low freq) → Follows input → PASSES

CUTOFF FREQUENCY (fc):
fc = 1 / (2πRC)

Below fc: Signal passes (~100% transmission)
At fc: Signal reduced to 70.7%
Above fc: Signal blocked (increasing attenuation)

APPLICATIONS:
• Audio bass filters
• Noise reduction
• Power supply smoothing
• Anti-aliasing in ADCs"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("About RC Low-Pass Filter")
        dialog.geometry("500x500")
        dialog.configure(bg='#2b2b2b')
        
        text = tk.Text(dialog, wrap=tk.WORD, bg='#0a0a0a', fg='#ffff00',
                      font=('Arial', 10), padx=15, pady=15)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', about_text)
        text.config(state=tk.DISABLED)
        
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg='#4444ff', fg='white', font=('Arial', 10, 'bold'),
                 width=15, pady=5).pack(pady=10)
    
    def change_probe(self, event=None):
        self.probe_ch1 = self.ch1_combo.get()
        self.probe_ch2 = self.ch2_combo.get()
    
    def toggle_channel(self):
        self.show_ch1 = self.ch1_var.get()
        self.show_ch2 = self.ch2_var.get()
    
    def update_display(self):
        if not self.is_running:
            self.root.after(50, self.update_display)
            return
        
        time_span = self.time_div * 10 / 1000
        t = np.linspace(0, time_span, 2000)
        
        signals = self.simulator.simulate(self.circuit, t, self.frequency)
        
        if signals:
            probe_ch1_key = self.circuit.probe_points.get(self.probe_ch1, "input")
            probe_ch2_key = self.circuit.probe_points.get(self.probe_ch2, "output")
            
            signal_ch1 = signals.get(probe_ch1_key, np.zeros_like(t))
            signal_ch2 = signals.get(probe_ch2_key, np.zeros_like(t))
            
            trigger_idx = self.find_trigger_point(signal_ch1)
            t_display = (t[trigger_idx:] - t[trigger_idx]) * 1000
            signal_ch1 = signal_ch1[trigger_idx:]
            signal_ch2 = signal_ch2[trigger_idx:]
            
            if self.show_ch1:
                self.line_ch1.set_data(t_display, signal_ch1)
                self.line_ch1.set_visible(True)
            else:
                self.line_ch1.set_visible(False)
                
            if self.show_ch2:
                self.line_ch2.set_data(t_display, signal_ch2)
                self.line_ch2.set_visible(True)
            else:
                self.line_ch2.set_visible(False)
            
            self.ax.set_xlim(0, self.time_div * 10)
            self.ax.set_ylim(-self.volt_div * 5, self.volt_div * 5)
            self.trigger_line.set_ydata([self.trigger_level, self.trigger_level])
            
            self.ax.set_xlabel('Time (ms)', color='#00ff00', fontsize=10)
            self.ax.set_ylabel('Voltage (V)', color='#00ff00', fontsize=10)
            
            # Update frequency info
            fc = self.circuit.calculate_cutoff_frequency()
            if self.frequency < fc:
                status = f"BELOW Cutoff ({self.frequency} Hz < {fc:.0f} Hz) - Signal PASSES"
                self.freq_info_label.config(bg='#00aa00')
            elif self.frequency > fc * 1.5:
                status = f"ABOVE Cutoff ({self.frequency} Hz > {fc:.0f} Hz) - Signal BLOCKED"
                self.freq_info_label.config(bg='#aa0000')
            else:
                status = f"NEAR Cutoff ({self.frequency} Hz ≈ {fc:.0f} Hz) - Transition"
                self.freq_info_label.config(bg='#aaaa00')
            
            self.freq_info_label.config(text=status)
            
            self.ax.set_title(f'{self.circuit.name} @ {self.frequency} Hz', 
                            color='#ffaa00', fontsize=11, fontweight='bold')
            
            self.ax.legend(loc='upper right', facecolor='#1a1a1a', 
                         edgecolor='#00ff00', labelcolor='#00ff00')
            
            self.canvas.draw()
        
        self.root.after(50, self.update_display)
    
    def find_trigger_point(self, signal):
        if len(signal) < 2:
            return 0
        for i in range(len(signal) - 1):
            if signal[i] <= self.trigger_level < signal[i + 1]:
                return i
        return 0
    
    def update_time_div(self, val):
        self.time_div = float(val)
    
    def update_volt_div(self, val):
        self.volt_div = float(val)
    
    def update_frequency(self, val):
        self.frequency = float(val)
    
    def update_trigger(self, val):
        self.trigger_level = float(val)
    
    def toggle_run(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.run_button.config(text="STOP", bg='#ff4444')
        else:
            self.run_button.config(text="RUN", bg='#44ff44')

def main():
    root = tk.Tk()
    app = CROEmulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
