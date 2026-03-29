FROM python:3.11-slim

WORKDIR /app

COPY api.py .

RUN pip install --no-cache-dir fastapi uvicorn elasticsearch==8.13.2 requests prometheus-client

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
