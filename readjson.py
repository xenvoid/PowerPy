import json
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

data = {
    "name": "Alice",
    "age": 30,
    "height": 1.65,
    "is_student": True,
    "city": "London"
}

# Write JSON
#with open("data.json", "w") as f:
#    json.dump(data, f, indent=2)

# Read JSON
with open("C:/Pythonprojects/powerpy/data.json", "r") as f:
    loaded = json.load(f)
    print(loaded)
    for entry in loaded:
        print(entry["Cpu"], entry["Gpu"])



# Extract Cpu and Gpu data
cpu_samples = []
gpu_samples = []

for entry in loaded:
    cpu_samples.append(entry["Cpu"])
    gpu_samples.append(entry["Gpu"])

# Convert to NumPy arrays
x_data = np.arange(len(cpu_samples))  
y_data = np.array(cpu_samples)

# Fit the model
def model(x, a, b, c):
    return a * x**2 + b * x + c


params, _ = curve_fit(model, x_data, y_data, p0=[10, 1, 0])
print("Fitted parameters:", params)


fitted_y = model(x_data, *params)

# Generate smooth x values (e.g. 10x more points)
x_smooth = np.linspace(min(x_data), max(x_data), 500)
fitted_y_smooth = model(x_data, *params)

# Plot original and smoothed fitted data
plt.figure(figsize=(10,5))
plt.scatter(x_data, y_data, label="Data", color="blue")
plt.plot(x_smooth, fitted_y_smooth, label="Smoothed Curve", color="orange")
plt.legend()
plt.xlabel("Samples")
plt.ylabel("Power (W)")
plt.title("Consumption kWh")
plt.grid(True)
plt.show()
