FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY esfs-1-d224.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "esfs-1-d224.py"]
