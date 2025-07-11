FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tavi-5-28d9.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavi-5-28d9.py"]
