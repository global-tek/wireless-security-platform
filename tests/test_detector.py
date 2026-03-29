from fastapi.testclient import TestClient

from conftest import load_module


def test_detect_flags_unknown_ssid():
    detector = load_module(
        "detector_module", "services/detection-engine/detector.py"
    )

    alerts = detector.detect([{"ssid": "CorpWifi"}, {"ssid": "EvilTwin"}])

    assert len(alerts) == 1
    assert alerts[0]["type"] == "unknown_network"
    assert alerts[0]["ssid"] == "EvilTwin"


def test_detect_endpoint_returns_count():
    detector = load_module(
        "detector_endpoint_module", "services/detection-engine/detector.py"
    )
    client = TestClient(detector.app)

    response = client.post(
        "/detect",
        json={"networks": [{"ssid": "OfficeNet"}, {"ssid": "GuestWifi"}]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["alerts"][0]["ssid"] == "GuestWifi"
