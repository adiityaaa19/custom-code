FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sef-1-acf3.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "sef-1-acf3.py"]
