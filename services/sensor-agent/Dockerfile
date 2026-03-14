FROM python:3.11

WORKDIR /app

COPY sensor_agent.py .

RUN pip install requests

CMD ["python","sensor_agent.py"]