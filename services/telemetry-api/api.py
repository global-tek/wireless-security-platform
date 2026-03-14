from fastapi import FastAPI
from elasticsearch import Elasticsearch

app = FastAPI()

es = Elasticsearch("http://elasticsearch:9200")

@app.post("/telemetry")
def ingest(data:dict):

    es.index(index="wifi-telemetry", body=data)

    return {"status":"ok"}