FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tavi-3-1ab5.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavi-3-1ab5.py"]
