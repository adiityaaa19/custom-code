FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY stri-3-f7e3.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "stri-3-f7e3.py"]
