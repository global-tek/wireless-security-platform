import subprocess
import time
import json
import requests

API="http://telemetry-api:8000/telemetry"

def scan():

    output = subprocess.check_output(
        ["iw","dev","wlan0","scan"]
    ).decode()

    data = {
        "timestamp": time.time(),
        "scan": output
    }

    requests.post(API,json=data)

def run():

    while True:
        scan()
        time.sleep(60)

if __name__ == "__main__":
    run()