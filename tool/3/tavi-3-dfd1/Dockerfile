FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tavi-3-dfd1.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavi-3-dfd1.py"]
