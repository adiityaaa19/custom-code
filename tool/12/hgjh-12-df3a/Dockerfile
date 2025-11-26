FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY hgjh-12-df3a.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "hgjh-12-df3a.py"]
