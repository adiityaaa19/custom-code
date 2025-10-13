FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sql5-1-0e64.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "sql5-1-0e64.py"]
