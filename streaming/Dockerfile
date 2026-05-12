FROM python:3.9-slim

WORKDIR /app

RUN pip install requests confluent-kafka

COPY producer.py .

CMD ["python", "producer.py"]