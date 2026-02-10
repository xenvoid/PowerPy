import json
import matplotlib.pyplot as plt
import numpy as np
import os
import time
from scipy.optimize import curve_fit

# Exponential decay model: one variable, 3 parameters
def model(x, a, b, c):
    return a * np.exp(-b * x) + c

plt.ion()
fig, ax = plt.subplots()

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

while True:
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        cpu = [entry["Cpu"] for entry in data]
        if len(cpu) < 3:
            continue  # need enough points to fit

        x_data = np.arange(len(cpu))
        y_data = np.array(cpu)

        # Fit the model
        params, _ = curve_fit(model, x_data, y_data, p0=[max(y_data), 0.1, min(y_data)])
        fitted_y = model(x_data, *params)

        # Smooth curve
        x_smooth = np.linspace(min(x_data), max(x_data), 500)
        fitted_y_smooth = model(x_smooth, *params)

        # Plot
        ax.clear()
        ax.scatter(x_data, y_data, label="Raw Data", color="blue")
        ax.plot(x_smooth, fitted_y_smooth, label="Fitted Curve", color="orange")
        ax.set_title("Live CPU (Exponential Fit)")
        ax.set_xlabel("Sample")
        ax.set_ylabel("CPU")
        ax.legend()
        ax.grid(True)
        plt.draw()
        plt.pause(1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
