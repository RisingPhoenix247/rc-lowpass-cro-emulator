# RC Low-Pass Filter CRO Emulator

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

A complete cathode ray oscilloscope (CRO) emulator with interactive circuit builder for designing and testing RC low-pass filters with square wave inputs.

## 🌟 Features

- ⚡ **Interactive Circuit Builder** - Add resistors, capacitors, and voltage sources
- 📊 **Real-time Oscilloscope** - Dual-channel visualization with trigger control
- 🔊 **Square Wave Input** - Test filter response with adjustable frequency (100Hz - 10kHz)
- 💾 **Save/Load Circuits** - Store and share your designs as JSON files
- 📐 **Automatic Calculations** - Cutoff frequency computed in real-time
- 🎓 **Educational Tool** - Perfect for learning electronics and signal processing

## 📸 Screenshots

![Main Window](docs/screenshots/main_window.png)

## 📋 Requirements

- Python 3.8 or higher
- tkinter (usually comes with Python)
- numpy
- matplotlib

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/rc-lowpass-cro-emulator.git
cd rc-lowpass-cro-emulator

# Install dependencies
pip install -r requirements.txt

# Run the application
python oscilloscope.py
```

### First Run

1. **Launch the application** - A default RC low-pass filter is already loaded
2. **Adjust frequency slider** - Move between 100Hz and 10kHz
3. **Observe the filtering** - Watch how output smooths at high frequencies

## 🎯 How It Works

### RC Low-Pass Filter Basics

Input ──[Resistor]──┬── Output
│
[Capacitor]
│
GND

**Key Concept:**
- **Low frequencies** (< cutoff) → Signal **PASSES** ✅
- **High frequencies** (> cutoff) → Signal **BLOCKED** ❌

### Cutoff Frequency

fc = 1 / (2πRC)

**Example:** R=1kΩ, C=100nF → fc ≈ 1591 Hz

## 📚 Usage Guide

### Building Your Circuit

1. **Add Components:**
   - Click "Add Resistor" → Enter value (e.g., `1000` for 1kΩ)
   - Click "Add Capacitor" → Enter value (e.g., `100e-9` for 100nF)
   - Click "Add Voltage Source" → Enter amplitude (e.g., `5` for 5V)

2. **Add Probe Points:**
   - Click "Add Probe Point"
   - Choose signal: `input`, `output`, `resistor`, or `capacitor`

3. **Save Your Work:**
   - File → Save Circuit
   - Choose location and filename

### Testing Different Frequencies

| Frequency | vs Cutoff | Expected Behavior |
|-----------|-----------|-------------------|
| 100 Hz    | Below     | Output ≈ Input    |
| 1591 Hz   | At cutoff | Output = 0.707 × Input |
| 5000 Hz   | Above     | Heavy smoothing   |

## 🔬 Example Experiments

### Experiment 1: Verify Cutoff Frequency

1. Use default circuit (fc ≈ 1591 Hz)
2. Set frequency to 1000 Hz → Output follows input
3. Set frequency to 5000 Hz → Output heavily attenuated

### Experiment 2: Change Cutoff

1. Remove R1, add new resistor with value 10000
2. Cutoff drops to ~159 Hz
3. Now 1000 Hz is ABOVE cutoff!

### Experiment 3: Time Constant

τ = RC = 1000 × 100e-9 = 100 microseconds
This is how fast the capacitor charges/discharges

## 📁 Example Circuits

Load pre-built examples from the `examples/` folder:

- **default_filter.json** - Standard 1.6kHz cutoff filter
- **high_cutoff.json** - 15.9kHz cutoff (tight filtering)
- **low_cutoff.json** - 159Hz cutoff (heavy smoothing)

## 🎓 Educational Value

Perfect for learning:
- ✅ Filter theory and frequency response
- ✅ Time constants and exponential charging
- ✅ Transfer functions and Bode plots
- ✅ Oscilloscope operation and triggering
- ✅ Circuit design and component selection

## 🛠️ Technical Details

- **Simulation Rate:** 2000 samples per update
- **Update Frequency:** 20 FPS (50ms refresh)
- **Time Base:** 0.1ms to 10ms per division
- **Voltage Scale:** 0.5V to 10V per division
- **Trigger:** Rising edge detection

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by classic analog oscilloscopes and CRT displays
- Built for educational purposes in electronics and signal processing
- Thanks to the Python community for excellent libraries (NumPy, Matplotlib, Tkinter)

## 📧 Contact

RisingPhoenix247 

Project Link: [https://github.com/RisingPhoenix247/rc-lowpass-cro-emulator](https://github.com/RisingPhoenix247/rc-lowpass-cro-emulator)

## ⭐ Star History

If you find this project helpful, please consider giving it a star!

---

**Made with ❤️ for electronics enthusiasts and students**
