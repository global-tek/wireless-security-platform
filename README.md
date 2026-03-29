# Wireless Security Platform

This repository contains a small, containerized prototype for wireless telemetry ingestion and basic network anomaly detection.

## Components

- `sensor-agent`: scans wifi data (`iw dev <iface> scan`), extracts SSIDs, and posts telemetry to the API.
- `detection-engine`: evaluates scanned networks against a known list and returns alerts for unknown SSIDs.
- `telemetry-api`: receives telemetry, calls the detection engine, enriches records with alerts, and stores documents in Elasticsearch.
- `telemetry-api`: installs an index template/mapping for `wifi-telemetry*` before indexing documents.
- `prometheus`: scrapes metrics exposed by `telemetry-api` at `/metrics`.
- `grafana`, `kibana`, `elasticsearch`: observability and storage stack.

## Data Flow

1. `sensor-agent` collects scan output every 60 seconds.
2. `sensor-agent` posts JSON payloads to `POST /telemetry`.
3. `telemetry-api` calls `detection-engine` at `POST /detect`.
4. `telemetry-api` stores enriched data in Elasticsearch index `wifi-telemetry`.
5. Prometheus scrapes telemetry API metrics.

## Run Locally

```bash
docker compose build
docker compose up -d
```

Useful endpoints:

- Telemetry API health: `http://localhost:8000/healthz`
- Telemetry API metrics: `http://localhost:8000/metrics`
- Detection engine health: `http://localhost:8001/healthz`
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Kubernetes Deployment

Apply all manifests:

```bash
kubectl apply -f k8s/
```

Resources included:

- `namespace.yaml`
- `elasticsearch.yaml`
- `kibana.yaml`
- `grafana.yaml`
- `prometheus-configmap.yaml`
- `prometheus.yaml`
- `detection-engine.yaml`
- `telemetry-api.yaml`
- `sensor-agent.yaml`

## Testing

Run locally:

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Repository Layout

```text
wireless-security-platform/
    docker-compose.yml
    Makefile
    monitoring/
        prometheus.yml
    k8s/
        namespace.yaml
        elasticsearch.yaml
        kibana.yaml
        grafana.yaml
        prometheus-configmap.yaml
        prometheus.yaml
        detection-engine.yaml
        telemetry-api.yaml
        sensor-agent.yaml
    tests/
        conftest.py
        test_detector.py
        test_telemetry_api.py
    services/
        sensor-agent/
            Dockerfile
            sensor_agent.py
        detection-engine/
            Dockerfile
            detector.py
        telemetry-api/
            Dockerfile
            api.py
```

## Notes

- The known network allowlist is defined in `services/detection-engine/detector.py`.
- Local compose uses Elasticsearch 8 with security/TLS disabled for development simplicity.