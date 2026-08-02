FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data ./data
COPY features ./features
COPY serving ./serving
COPY monitoring ./monitoring
COPY model_store ./model_store
COPY feature_store ./feature_store

EXPOSE 8000

CMD ["uvicorn", "serving.api:app", "--host", "0.0.0.0", "--port", "8000"]
