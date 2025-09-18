FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY dsdf-1-8991.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "dsdf-1-8991.py"]
