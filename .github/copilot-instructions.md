# PowerPy: System Power Monitoring & Analysis

## Project Overview

PowerPy is a **Windows-based real-time power consumption monitoring tool** that captures CPU and GPU power draw, stores historical data, and provides live visualization with curve fitting analysis. The system integrates LibreHardwareMonitor (C#/.NET) as a backend service for hardware monitoring.

## Architecture & Data Flow

### Core Components

1. **power.py** (main script)
   - Launches and manages LibreHardwareMonitor (`tools/LibreHardwareMonitor.exe`) as a background service
   - Polls LHM's REST API (`http://localhost:8085/data.json`) every 1 second
   - Extracts CPU Package and GPU Package power values from nested sensor hierarchy
   - Accumulates samples and computes running averages, max values, and energy (kWh) estimates
   - **Only logs changes**: Uses `last_cpu` and `last_gpu` tracking to avoid duplicate entries when values don't change
   - Stores data to `data.json` in append mode with structure: `{"Cpu": float, "Gpu": float, "S": int}`
   - Includes static power estimate for non-monitored components (SSDs, HDDs, fans, motherboard base)

2. **LibreHardwareMonitor (LHM)**
   - External .NET application bundled in `tools/` directory
   - Runs as HTTP service on `localhost:8085`
   - Returns hierarchical JSON with sensor tree containing "Package", "GPU Package", and "Power" type nodes
   - Process lifecycle: Started by power.py, killed on exit or keyboard interrupt

3. **Data Storage** (`data.json`)
   - Persistent JSON array of power readings
   - Append-only pattern: new readings added, file never truncated
   - Used by analysis/visualization scripts
   - Risk: File grows unbounded; no cleanup mechanism documented

### Analysis & Visualization

- **live_json.py**: Real-time quadratic curve fitting + matplotlib live plotting
  - Uses `safe_read_json()` with 5 retries and 0.15s delays to handle concurrent access from power.py
  - Fits model: $y = ax^2 + bx + c$ where x is time in seconds
  - Redraws plot every 1 second
  
- **importjson.py** & **readjson.py**: Experimental analysis scripts
  - Try exponential decay and polynomial models
  - Different file paths and data extraction approaches

## Critical Implementation Details

### Process Management
- LibreHardwareMonitor must be running before API calls succeed
- `wait_for_lhm(timeout=15)` polls API with 1s intervals until response or timeout
- Process tracking via `psutil.process_iter(['pid', 'name'])` to find and kill LHM
- **Important**: Set `stdout=subprocess.DEVNULL` and `stderr=subprocess.DEVNULL` to prevent console spam

### Data Collection Strategy
- **Change-based logging**: Only append to data.json when CPU OR GPU value changes from previous sample
  - Counter `s` increments for each change event (not time-based)
  - Reduces file bloat during idle periods
- String parsing required: LHM returns values like `"45.2 W"`, must strip and convert to float
- Missing data handling: Returns empty dict from `get_cpu_gpu_power()` on exceptions; defaults to 0.0

### Static Power Estimation
```python
SSD_COUNT = 2      # 4W per drive
HDD_COUNT = 1      # ~0W (mostly idle)
FAN_COUNT = 3      # 2W per fan
EST_MB = 30        # Motherboard baseline
```
Adjust these constants based on actual hardware; currently estimates ~42W base load.

### JSON Concurrency Pattern
Shared file access between power.py (writer) and live_json.py (reader) requires:
- Retry logic with exponential backoff or fixed delays
- Try/except for `json.JSONDecodeError` during partial writes
- **No file locking mechanism documented** — potential data corruption if both write simultaneously

## Development Workflows

### Running the Monitor
```powershell
# Via batch file (simplest)
.\power.bat

# Via Python directly
python power.py

# Via admin VBS (elevation script available)
cscript run_admin.vbs
```

### Real-Time Analysis
Terminal 1: `python power.py` (data collection)  
Terminal 2: `python live_json.py` (live visualization)

### Testing Data Collection
- `fromscipy.py`: Generates synthetic oscillating power data for testing visualization without hardware
- Mock values: CPU = 30 + 20*sin(t), GPU = 25 + 15*cos(t)

## Project Conventions & Patterns

### Naming & Constants
- Script files use action verbs: `power.py`, `importjson.py`, `readjson.py`, `live_json.py`
- System config as module-level constants (not config files)
- Data structure keys: lowercase single words (`"Cpu"`, `"Gpu"`, `"S"` for sample count)

### Global State
- Uses global accumulators: `cpu_total`, `gpu_total`, `count`, `total_max`, `pwdata_log`
- Local variable tracking for change detection: `last_cpu`, `last_gpu`, `s` (sample counter)
- Long-running process pattern: infinite `while True` loop with `KeyboardInterrupt` handler

### Error Handling
- Graceful degradation: Missing LHM returns `{}`, scripts continue with zeros
- File I/O: Check `os.path.exists()` before read, create if missing for write
- Retry loops for transient failures (JSON read polling)

## Integration Points & Dependencies

### External Dependencies
- **LibreHardwareMonitor**: Bundled executable, no pip installation
- **requests**: HTTP calls to LHM API
- **psutil**: Process management (kill LHM)
- **numpy, scipy**: Data fitting (`curve_fit`)
- **matplotlib**: Live plotting with `ion()` mode

### File System Layout
```
powerpy/
├── power.py              # Main monitor script
├── live_json.py          # Real-time visualization
├── importjson.py         # Exponential fit variant
├── readjson.py           # Analysis/visualization
├── fromscipy.py          # Synthetic data generator
├── power.bat             # Batch launcher
├── run_admin.vbs         # Admin elevation script
├── data.json             # Persistent power readings (auto-created)
├── data.jsonold          # Backup of old data
├── tools/                # LibreHardwareMonitor + dependencies
│   └── LibreHardwareMonitor.exe
└── .github/
    └── copilot-instructions.md
```

### Data Flow Summary
```
LHM.exe (HTTP :8085)
    ↓ (requests.get)
power.py (polls every 1s)
    ↓ (filters changes, calculates stats)
data.json (append-only)
    ↓ (safe_read_json retry loop)
live_json.py & analysis scripts (visualization)
```

## Common Tasks for AI Agents

### Extending Power Monitoring
- Add new sensor types: Modify `find_power_values()` to check other `sensor_type` values
- Adjust collection frequency: Change `time.sleep(1)` intervals
- Add new metrics: Extend the data structure (e.g., `"Temp": cpu_temp`)

### Improving Data Visualization
- Swap curve fitting models: Replace quadratic ($ax^2 + bx + c$) with exponential, polynomial, or custom functions
- Change plot update frequency: Modify matplotlib `plt.pause()` interval
- Add multi-panel plots: Use `plt.subplots(1, 2)` for CPU vs GPU comparison

### Handling Data Volume
- Implement data cleanup: Archive old data.json entries or implement rolling window
- Convert to time-indexed format instead of sample counter `"S"`
- Use structured logging (e.g., CSV) instead of JSON for better streaming

## Known Limitations & Gaps

1. **No data retention policy** — data.json grows indefinitely
2. **No formal logging** — only print statements; logs.txt files remain empty
3. **Race conditions possible** — concurrent JSON read/write without file locking
4. **Hardcoded paths** — Full absolute paths in analysis scripts; limits portability
5. **Static power estimate** — Requires manual calibration per machine
6. **No configuration file** — All settings are hardcoded constants

## AI Agent Quick Start

When working on this codebase:
1. **Always run LHM first** — power.py will fail silently if LHM isn't available
2. **Understand the 3-step flow**: LHM (hardware) → power.py (collection) → analysis (visualization)
3. **Change-based logging** is intentional — don't add samples on every iteration, only on value changes
4. **File access synchronization** requires careful retry logic — concurrent access is not thread-safe
5. **Test with fromscipy.py** if hardware sensors unavailable — generates synthetic data with same structure
