FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY dfgd-1-6e34.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "dfgd-1-6e34.py"]
