FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY awdw-1-d3cc.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "awdw-1-d3cc.py"]
