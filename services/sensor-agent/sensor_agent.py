import os
import re
import subprocess
import time

import requests

API = os.getenv("TELEMETRY_API", "http://telemetry-api:8000/telemetry")
INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
IFACE = os.getenv("WIFI_INTERFACE", "wlan0")


def parse_networks(scan_output: str):
    ssids = []
    for line in scan_output.splitlines():
        match = re.match(r"\s*SSID:\s*(.*)", line)
        if not match:
            continue
        ssid = match.group(1).strip()
        if ssid and ssid not in ssids:
            ssids.append(ssid)

    return [{"ssid": ssid} for ssid in ssids]


def collect_scan_output():
    try:
        return subprocess.check_output(["iw", "dev", IFACE, "scan"]).decode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Keep the loop alive where wifi tooling is unavailable.
        return ""


def scan():
    output = collect_scan_output()
    data = {
        "timestamp": time.time(),
        "networks": parse_networks(output),
        "raw_scan": output,
    }

    try:
        requests.post(API, json=data, timeout=10)
    except requests.RequestException:
        pass


def run():
    while True:
        scan()
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
