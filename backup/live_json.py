import json
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import time


# Function to read safe jSON file
import json
import time

def safe_read_json(path, retries=5, delay=0.15):
    for _ in range(retries):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            time.sleep(delay)
    return None

#------------------ Live Plotting ------------------

plt.ion()
fig, ax = plt.subplots()

def model(x, a, b, c):
    return a * x**2 + b * x + c

while True:
    try:
        # with open(r"C:\Users\xenvo\Pythonprojects\powerpy\data.json", "r") as f:
        #     data = json.load(f)

        data = safe_read_json(r"C:\Users\xenvo\Pythonprojects\powerpy\data.json")
        if not data:
            print("Failed to read data file.")
            time.sleep(1)
            continue

        cpu = [entry["Cpu"] for entry in data]
        time_s = [entry["S"] for entry in data]
        #x = np.arange(len(cpu))
        x = np.array(time_s)
        # Fit model
        params, _ = curve_fit(model, x, cpu, p0=[10, 1, 0])

        # Smooth curve using x values
        x_smooth = np.linspace(min(x), max(x), 500)
        fitted_y_smooth = model(x_smooth, *params)

        # Plot
        ax.clear()
        #ax.scatter(x, cpu, label="CPU (W)", color="blue",s = 1)
        ax.plot(x_smooth, fitted_y_smooth, label="curve", color="orange",lw = 5)
        ax.set_title("Live CPU Wattage")
        ax.set_xlabel("S")
        ax.set_ylabel("W")
        ax.legend()
        ax.grid(True)
        plt.draw()
        plt.pause(1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
