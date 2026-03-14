import json

KNOWN_NETWORKS = [
    "CorpWifi",
    "OfficeNet"
]

def detect(scan):

    alerts=[]

    for network in scan:

        if network["ssid"] not in KNOWN_NETWORKS:

            alerts.append({
                "type":"unknown_network",
                "ssid":network["ssid"]
            })

    return alerts