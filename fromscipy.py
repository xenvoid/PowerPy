from scipy.optimize import curve_fit
import numpy as np

import math, time

t = 0
while True:
    cpu = 30 + 20 * math.sin(t)  # oscillates between 10 and 50
    gpu = 25 + 15 * math.cos(t)
    print(f"CPU: {cpu:.1f} W | GPU: {gpu:.1f} W")
    t += 0.1
    time.sleep(0.5)

