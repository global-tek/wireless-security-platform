import os
import time

import requests
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = FastAPI()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
DETECTION_URL = os.getenv(
    "DETECTION_URL", "http://detection-engine:8001/detect"
)

INGEST_TOTAL = Counter(
    "telemetry_ingest_total", "Total telemetry payloads ingested"
)
INGEST_ERRORS_TOTAL = Counter(
    "telemetry_ingest_errors_total", "Total telemetry payload failures"
)
ALERT_TOTAL = Counter("telemetry_alert_total", "Total alerts generated")
INGEST_LATENCY_SECONDS = Histogram(
    "telemetry_ingest_latency_seconds", "Latency for telemetry ingestion"
)

es = Elasticsearch(ELASTICSEARCH_URL)
INDEX_NAME = "wifi-telemetry"
TEMPLATE_NAME = "wifi-telemetry-template"


def ensure_index_template():
    es.indices.put_index_template(
        name=TEMPLATE_NAME,
        body={
            "index_patterns": ["wifi-telemetry*"],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                },
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "double"},
                        "raw_scan": {"type": "text"},
                        "alert_count": {"type": "integer"},
                        "networks": {
                            "type": "nested",
                            "properties": {
                                "ssid": {"type": "keyword"},
                            },
                        },
                        "alerts": {
                            "type": "nested",
                            "properties": {
                                "type": {"type": "keyword"},
                                "ssid": {"type": "keyword"},
                            },
                        },
                    }
                },
            },
        },
    )


def ensure_index_exists():
    ensure_index_template()
    es.options(ignore_status=400).indices.create(index=INDEX_NAME)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/telemetry")
def ingest(data: dict):
    started = time.time()
    INGEST_TOTAL.inc()

    alerts = []
    try:
        detection_response = requests.post(
            DETECTION_URL,
            json={"networks": data.get("networks", [])},
            timeout=5,
        )
        detection_response.raise_for_status()
        alerts = detection_response.json().get("alerts", [])
    except requests.RequestException:
        INGEST_ERRORS_TOTAL.inc()

    enriched_doc = {
        **data,
        "alerts": alerts,
        "alert_count": len(alerts),
    }

    try:
        ensure_index_exists()
        es.index(index=INDEX_NAME, document=enriched_doc)
    except Exception:
        INGEST_ERRORS_TOTAL.inc()
        INGEST_LATENCY_SECONDS.observe(time.time() - started)
        return {
            "status": "degraded",
            "alerts": alerts,
            "alert_count": len(alerts),
            "error": "failed_to_index",
        }

    ALERT_TOTAL.inc(len(alerts))
    INGEST_LATENCY_SECONDS.observe(time.time() - started)

    return {"status": "ok", "alerts": alerts, "alert_count": len(alerts)}
