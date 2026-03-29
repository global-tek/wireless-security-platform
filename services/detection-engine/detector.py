from fastapi import FastAPI

KNOWN_NETWORKS = {
    "CorpWifi",
    "OfficeNet",
}

app = FastAPI()


def detect(networks):
    alerts = []

    for network in networks:
        ssid = network.get("ssid")
        if not ssid:
            continue

        if ssid not in KNOWN_NETWORKS:
            alerts.append(
                {
                    "type": "unknown_network",
                    "ssid": ssid,
                }
            )

    return alerts


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/detect")
def detect_endpoint(data: dict):
    networks = data.get("networks", [])
    alerts = detect(networks)
    return {"alerts": alerts, "count": len(alerts)}
