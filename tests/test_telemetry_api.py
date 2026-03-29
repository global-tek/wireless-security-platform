from fastapi.testclient import TestClient

from conftest import load_module


class FakeDetectionResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeIndices:
    def put_index_template(self, name, body):
        return {"name": name, "body": body}

    def create(self, index):
        return {"index": index}


class FakeES:
    def __init__(self):
        self.indices = FakeIndices()
        self.documents = []

    def options(self, **kwargs):
        return self

    def index(self, index, document):
        self.documents.append({"index": index, "document": document})
        return {"result": "created"}


class FailingES(FakeES):
    def index(self, index, document):
        raise RuntimeError("index failed")


def test_ingest_success(monkeypatch):
    api = load_module("telemetry_api_module", "services/telemetry-api/api.py")

    monkeypatch.setattr(api, "es", FakeES())
    monkeypatch.setattr(
        api.requests,
        "post",
        lambda url, json, timeout: FakeDetectionResponse(
            {"alerts": [{"type": "unknown_network", "ssid": "RogueAP"}]}
        ),
    )

    client = TestClient(api.app)
    response = client.post(
        "/telemetry",
        json={"timestamp": 1.0, "networks": [{"ssid": "RogueAP"}]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["alert_count"] == 1


def test_ingest_degraded_when_index_fails(monkeypatch):
    api = load_module("telemetry_api_module", "services/telemetry-api/api.py")

    monkeypatch.setattr(api, "es", FailingES())
    monkeypatch.setattr(
        api.requests,
        "post",
        lambda url, json, timeout: FakeDetectionResponse({"alerts": []}),
    )

    client = TestClient(api.app)
    response = client.post(
        "/telemetry",
        json={"timestamp": 1.0, "networks": []},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["error"] == "failed_to_index"


def test_integration_with_detection_engine(monkeypatch):
    detector = load_module(
        "detector_integration_module", "services/detection-engine/detector.py"
    )
    api = load_module("telemetry_api_module", "services/telemetry-api/api.py")

    detector_client = TestClient(detector.app)

    def bridged_detection_post(url, json, timeout):
        response = detector_client.post("/detect", json=json)
        return FakeDetectionResponse(response.json())

    monkeypatch.setattr(api, "es", FakeES())
    monkeypatch.setattr(api.requests, "post", bridged_detection_post)

    client = TestClient(api.app)
    response = client.post(
        "/telemetry",
        json={
            "timestamp": 1.0,
            "networks": [{"ssid": "CorpWifi"}, {"ssid": "BadAP"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["alert_count"] == 1
    assert payload["alerts"][0]["ssid"] == "BadAP"
