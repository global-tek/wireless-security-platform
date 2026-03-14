wireless-security-platform/

README.md
Makefile
docker-compose.yml

.github/
└── workflows/
    └── ci.yml

services/
├── sensor-agent/
│   ├── Dockerfile
│   └── sensor_agent.py
│
├── detection-engine/
│   ├── Dockerfile
│   └── detector.py
│
└── telemetry-api/
    ├── Dockerfile
    └── api.py

k8s/
├── namespace.yaml
├── sensor-agent.yaml
├── detection-engine.yaml
└── telemetry-api.yaml

monitoring/
├── prometheus.yml
└── grafana-datasource.yaml