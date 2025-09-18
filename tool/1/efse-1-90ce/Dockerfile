FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt || true
COPY efse-1-90ce.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "efse-1-90ce.py"]
