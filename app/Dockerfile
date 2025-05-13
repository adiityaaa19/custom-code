FROM python:3.10-slim

WORKDIR /app

COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .env .env

RUN pip install gunicorn

EXPOSE 8080

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:$PORT", "main:app"]
