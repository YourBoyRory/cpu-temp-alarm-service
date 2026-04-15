#!/usr/bin/env python3

import time
import os
import configparser

def find_package_sensor():
    base = "/sys/class/hwmon"
    sensor_name = "Package id 0"
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
                    if f.read().strip() == sensor_name:
                        return label_path.replace("_label", "_input")
    raise RuntimeError(f"{sensor_name} sensor not found")

def read_config():
    sys_config_path = f"/etc/cpu-alarm-service/config.ini"
    cwd_path = os.path.join(os.getcwd(), "config.ini")
    config = configparser.ConfigParser()
    if os.path.isfile(cwd_path):
        config.read(cwd_path)
        print(f"Using config: {cwd_path}")
    elif os.path.isfile(sys_config_path):
        config.read(sys_config_path)
        print(f"Using config: {sys_config_path}")
    return config

def get_temp(probe):
    with open(probe, "r") as f:
        return int(f.read().strip())

config = read_config()
TEMP_PATH = config.get("temp", "path", fallback="auto")
if TEMP_PATH == "auto": TEMP_PATH = find_package_sensor()
THRESHOLD = int(config.get("temp", "threshold", fallback=92000))
INTERVAL = float(config.get("alarm", "interval", fallback=2000))
SEPERATOR = INTERVAL//4
print(f"Monitor started on {TEMP_PATH}")

while True:
    try:
        temp = get_temp(TEMP_PATH)
        if temp >= THRESHOLD:
            print(f"Above Threshold: {temp/1000:.1f}°C")
            os.system(f"beep -l {INTERVAL-SEPERATOR}")
            time.sleep(SEPERATOR//1000)
        else:
            time.sleep(INTERVAL//1000)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
