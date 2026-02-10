import json
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.optimize import curve_fit

def safe_read_json(path, retries=1, delay=0.01):
    for _ in range(retries):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            time.sleep(delay)
    return None

def format_uptime(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

class LivePlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PowerPy Live Monitor")
        self.setGeometry(100, 100, 900, 700)
        
        # Create figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        
        # Create layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add canvas
        layout.addWidget(self.canvas)
        
        # Add stats row (Energy & Uptime)
        stats_layout = QHBoxLayout()
        self.energy_label = QLabel("Energy: 0.0000 kWh")
        self.uptime_label = QLabel("Uptime: 0.00 Hr")
        stats_layout.addWidget(self.energy_label)
        stats_layout.addWidget(self.uptime_label)
        layout.addLayout(stats_layout)
        
        # Add controls
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.exit_btn = QPushButton("Exit")
        
        self.start_btn.clicked.connect(self.start_plotting)
        self.stop_btn.clicked.connect(self.stop_plotting)
        self.exit_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.exit_btn)
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.running = False
        
        # Accumulators (same as power.py)
        self.cpu_total = 0.0
        self.gpu_total = 0.0
        self.count = 0
        self.start_time = None
        self.last_sample_count = 0
    
    def model(self, x, a, b, c):
        return a * x**2 + b * x + c
    
    def start_plotting(self):
        self.running = True
        self.start_time = time.time()
        
        # Clear the JSON file to start fresh
        with open(r"C:\Users\xenvo\Pythonprojects\powerpy\data.json", "w") as f:
            json.dump([], f)
        
        self.timer.start(1000)  # Update every 1 second
        self.status_label.setText("Status: Running...")
    
    def stop_plotting(self):
        self.running = False
        self.timer.stop()
        self.status_label.setText("Status: Stopped")
    
    def update_plot(self):
        try:
            data = safe_read_json(r"C:\Users\xenvo\Pythonprojects\powerpy\data.json")
            if not data:
                self.status_label.setText("Status: Failed to read data")
                return
            
            # Only update if new samples were added
            if len(data) <= self.last_sample_count:
                return
            
            self.last_sample_count = len(data)
            
            cpu = [entry["Cpu"] for entry in data]
            gpu = [entry["Gpu"] for entry in data]
            time_s = [entry["S"] for entry in data]
            x = np.array(time_s)
            
            # Calculate energy & uptime
            self.cpu_total = sum(cpu)
            self.gpu_total = sum(gpu)
            
            energy_kwh = (self.cpu_total + self.gpu_total) / 3_600_000
            elapsed_seconds = int(time.time() - self.start_time)
            
            # Update labels with formatted time
            self.energy_label.setText(f"Energy: {energy_kwh:.4f} kWh")
            self.uptime_label.setText(f"Uptime: {format_uptime(elapsed_seconds)}")
            
            # Fit model
            params, _ = curve_fit(self.model, x, cpu, p0=[10, 1, 0])
            
            # Smooth curve
            x_smooth = np.linspace(min(x), max(x), 500)
            fitted_y_smooth = self.model(x_smooth, *params)
            
            # Plot
            self.ax.clear()
            self.ax.plot(x_smooth, fitted_y_smooth, label="Fitted Curve", color="orange", lw=5)
            self.ax.set_title("Live CPU Wattage")
            self.ax.set_xlabel("Time (S)")
            self.ax.set_ylabel("Power (W)")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
            
            self.status_label.setText(f"Status: {len(cpu)} samples collected")
            
        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LivePlotWindow()
    window.show()
    sys.exit(app.exec_())
