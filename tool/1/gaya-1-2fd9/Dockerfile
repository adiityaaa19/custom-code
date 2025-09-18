FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY gaya-1-2fd9.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "gaya-1-2fd9.py"]
