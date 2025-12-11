FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY test-12-006a.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "test-12-006a.py"]
