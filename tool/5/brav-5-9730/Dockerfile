FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY brav-5-9730.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "brav-5-9730.py"]
