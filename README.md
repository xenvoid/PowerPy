# PowerPy

PowerPy is a Windows-based real-time power consumption monitoring and analysis tool. It collects CPU and GPU power data (via LibreHardwareMonitor), persists readings to JSON, and provides live visualization with curve fitting and simple energy/uptime metrics.

## Features
- Live plotting of CPU (and optionally GPU) power draw
- Persistent session data in `data.json`
- Simple curve fitting and energy/uptime calculations
- GUI built with PyQt5 and plotting with Matplotlib

## Requirements
- Windows (tested on Windows 10/11)
- Python 3.8+
- LibreHardwareMonitor running/configured to provide sensor data
- Python packages: `pyqt5`, `matplotlib`, `numpy`

Install Python packages (recommended in a virtualenv):

```powershell
python -m pip install --upgrade pip
pip install pyqt5 matplotlib numpy
```

## Quick Start

1. Ensure LibreHardwareMonitor (or your preferred sensor provider) is running and accessible on the machine.(or you can run as adminstrator power.bat)
2. From the repository root, run the live monitor GUI:

```powershell
python live_json.py
```

The GUI exposes controls to start/stop live plotting and shows a status line with samples collected.

## Important Files
- `live_json.py` — main GUI and live-plotting application (reads/writes `data.json`).
- `power.py` — helper code for collecting/writing sensor data (project-specific collection logic).
- `data.json` — persistent JSON store for session power samples.
- `power.bat`, `run_admin.vbs` — helper scripts for launching components with elevated privileges if needed.

## Usage Notes
- If you see JSON decode errors, delete or move `data.json` (the app will recreate it).
- The plotting window uses Matplotlib; resizing may trigger redraws.
- For reliable hardware readings, run LibreHardwareMonitor with administrator privileges.

## Contributing
PRs and issues are welcome. Please open an issue describing the problem or feature request before submitting large changes.



