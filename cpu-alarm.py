#!/usr/bin/env python3

import time
import os
import argparse
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

def alarm(pitch, interval, pulse_len, delay_len):
    os.system(f"beep -f {pitch} -r {interval//(pulse_len+delay_len)} -d {delay_len} -l {pulse_len}")

config = read_config()
TEMP_PATH = config.get("temp", "path", fallback="auto")
if TEMP_PATH == "auto": TEMP_PATH = find_package_sensor()
THRESHOLD = int(config.get("temp", "threshold", fallback=92000))
PITCH = int(config.get("alarm", "pitch", fallback=750))
PULSE_LEN = int(config.get("alarm", "pulse_len", fallback=900))
DELAY_LEN = int(config.get("alarm", "rest_len", fallback=100))
INTERVAL = int(config.get("temp", "interval", fallback=2000))
PULSE_TOTAL = PULSE_LEN+DELAY_LEN

def test():
    temp = get_temp(TEMP_PATH)
    print("\nCURRENT TEMPS:")
    print(f"    {temp/1000:.1f}°C / {THRESHOLD/1000:.1f}°C   ({temp}/{THRESHOLD})")
    above_threshold = temp >= THRESHOLD
    print(f"    Above Threshold:  {above_threshold}")
    print(f"    Polling Interval: {INTERVAL} ms\n")

    print("ALARM OPTIONS:")
    print(f"    pitch:            {PITCH} Hz")
    print(f"    pulse_len:        {PULSE_LEN} ms")
    print(f"    rest_len:         {DELAY_LEN} ms")
    print(f"    pulse_total:      {PULSE_TOTAL} ms")
    valid_interval = PULSE_TOTAL <= INTERVAL
    print(f"    Valid Interval:   {valid_interval}\n\n")

    i = 0
    test_count = 2
    while valid_interval and i in range(test_count):
        time_delta = round(time.time() * 1000)
        alarm(PITCH, INTERVAL, PULSE_LEN, DELAY_LEN)
        time_delta -= round(time.time() * 1000)
        i+=1
        print(f"[{i}/{test_count}] {(INTERVAL+time_delta)/1000} seconds remain on interval")
        if abs(time_delta) < INTERVAL*0.90 and i != test_count:
            time.sleep(max((INTERVAL+time_delta)/1000, 0))


def main():
    if INTERVAL < PULSE_TOTAL: raise RuntimeError(f"interval of {INTERVAL} too short! Must be not be smaller then {PULSE_TOTAL}")
    print(f"Monitor started on {TEMP_PATH}")
    while True:
        try:
            temp = get_temp(TEMP_PATH)
            if temp >= THRESHOLD:
                print(f"Above Threshold: {temp/1000:.1f}°C")
                time_delta = round(time.time() * 1000)
                alarm(PITCH, INTERVAL, PULSE_LEN, DELAY_LEN)
                time_delta -= round(time.time() * 1000)
                if abs(time_delta) < INTERVAL*0.90:
                    time.sleep(max((INTERVAL+time_delta)/1000, 0))
            else:
                time.sleep(INTERVAL/1000)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args = parser.parse_args()

if args.test:
    test()
else:
    main()
