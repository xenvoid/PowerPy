import requests
import time
import psutil
#Lhm Block#
import subprocess
import os
import time
import json

def stop_lhm():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and "LibreHardwareMonitor" in proc.info['name']:
            print("🛑 Stopping LibreHardwareMonitor...")
            proc.kill()
# Path to LibreHardwareMonitor executable
#LHM_PATH = r"\To\LibreHardwareMonitor.exe"

LHM_PATH = os.path.join(os.path.dirname(__file__), "tools", "LibreHardwareMonitor.exe")
def start_lhm():
    if not os.path.exists(LHM_PATH):
        raise FileNotFoundError("LibreHardwareMonitor.exe not found")

    # Start as background process
    subprocess.Popen([LHM_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Started LibreHardwareMonitor...")

    # Wait a bit for it to initialise
    time.sleep(5)

#############

# 🛠️ System constants — adjust as needed
SSD_COUNT = 2
HDD_COUNT = 1
FAN_COUNT = 3
RAM_GB = 32
EST_MB = 30  # Motherboard base power


def static_estimated_power():
    return (
        SSD_COUNT * 4 +
        HDD_COUNT * 0 +
        FAN_COUNT * 2 +
        EST_MB
    )

def find_power_values(node, results):
    if isinstance(node, dict):
        text = node.get("Text")
        value = node.get("Value")
        sensor_type = node.get("Type")

        if sensor_type == "Power" and text in ("Package", "GPU Package"):
            results[text] = value

        for child in node.get("Children", []):
            find_power_values(child, results)

def get_cpu_gpu_power():
    url = "http://localhost:8085/data.json"
    try:
        response = requests.get(url)
        data = response.json()
        results = {}
        find_power_values(data, results)
        return results
    except Exception as e:
        return {}

# Accumulators
cpu_total = 0.0
gpu_total = 0.0
count = 0
total_max = 0.0

def wait_for_lhm(timeout=15):
    print("⏳ Waiting for LibreHardwareMonitor API...")
    url = "http://localhost:8085/data.json"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print("✅ LibreHardwareMonitor is responding.")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ LHM API not available. Exiting.")
    return False



def writetofile_append(new_data):
    """Append a single sample to the JSON file"""
    filename = "data.json"
    
    # Load existing data
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # Append single sample
    if isinstance(new_data, dict):
        data.append(new_data)
    
    # Write back
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

import time
def main():
    start_lhm()
    if not wait_for_lhm():
        return
    
    EXTRA_STATIC = static_estimated_power()

    print(f"🔁 Monitoring with estimated system base: {EXTRA_STATIC:.1f} W")
    print("Press Ctrl+C to stop.\n")
    #global variables
    global cpu_total, gpu_total, count, total_max, pwdata, cpu
    pwdata_log = []
    

    # Before the loop
    start_time = time.time()
    last_cpu = last_gpu = None
    s = 0


    try:
        while True:
            power = get_cpu_gpu_power()
            cpu_str = power.get("Package")
            gpu_str = power.get("GPU Package")

            cpu = float(cpu_str.replace(" W", "")) if cpu_str else 0.0
            gpu = float(gpu_str.replace(" W", "")) if gpu_str else 0.0
            total = cpu + gpu
            total_max = max(total_max, total)

            cpu_total += cpu
            gpu_total += gpu
            count += 1
            s = count

            cpu_avg = cpu_total / count
            gpu_avg = gpu_total / count
            total_avg = cpu_avg + gpu_avg + EXTRA_STATIC

            energy_kwh = (cpu_total + gpu_total) / 3_600_000
            energy_uptime = count / 3600
            print(f"CPU: {cpu:.1f} W | GPU: {gpu:.1f} W | Est. Total: {total:.1f} W   || Avg: {total_avg:.1f} W | Energy: {energy_kwh:.4f} kWh | Uptime {round(energy_uptime,2)} Hr  {total_max}")

            # Append to memory
            pwdata_log.append({
                "Cpu": cpu,
                "Gpu": gpu,
                "S": s
            })
            
            # Write to file every second
            writetofile_append({
                "Cpu": cpu,
                "Gpu": gpu,
                "S": s
            })
            
            time.sleep(1)

    except KeyboardInterrupt:
        stop_lhm()
        print("\nStopped.")
    finally:    
        stop_lhm()    
        
        


if __name__ == "__main__":
    main()

