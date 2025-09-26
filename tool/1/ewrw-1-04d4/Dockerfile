FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ewrw-1-04d4.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "ewrw-1-04d4.py"]
