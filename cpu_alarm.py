import time
import os
import configparser
import subprocess
import threading

def find_package_sensor():
    base = "/sys/class/hwmon"
    for hwmon in os.listdir(base):
        hw_path = os.path.join(base, hwmon)
        try:
            with open(os.path.join(hw_path, "name")) as f:
                if f.read().strip() != "coretemp":
                    continue
        except:
            continue
        for file in os.listdir(hw_path):
            if file.endswith("_label"):
                label_path = os.path.join(hw_path, file)
                with open(label_path) as f:
                    if f.read().strip() == "Package id 0":
                        return label_path.replace("_label", "_input")
    raise RuntimeError("Package id 0 sensor not found")

def find_config():
    sys_config_path = f"/etc/temp-alarm/config.ini"
    cwd_path = os.path.join(os.getcwd(), "config.ini")
    if os.path.isfile(cwd_path):
        return cwd_path
    if os.path.isfile(sys_config_path):
        return sys_config_path
    raise FileNotFoundError(
        f"No config found in {cwd_path} or {sys_config_path}"
    )

config_path = find_config()
print(f"Using config: {config_path}")

config = configparser.ConfigParser()
config.read(config_path)

TEMP_PATH = config["temp"].get("path", "auto")
if TEMP_PATH == "auto": TEMP_PATH = find_package_sensor()
THRESHOLD = int(config["temp"].get("threshold", 92000))
INTERVAL = float(config["alarm"].get("interval", 2000))

print(f"Monitor started on {TEMP_PATH}")
def get_temp():
    with open(TEMP_PATH, "r") as f:
        return int(f.read().strip())

def alarm():
    os.system(f"beep -f 1000 -l {INTERVAL+100}")

while True:
    try:
        temp = get_temp()
        if temp >= THRESHOLD:
            print(f"Above Threshold: {temp/1000:.1f}°C")
            t = threading.Thread(target=alarm, daemon=True)
            t.start()
            triggered = True
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(INTERVAL//1000)
