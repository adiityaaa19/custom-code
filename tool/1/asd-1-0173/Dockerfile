FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY asd-1-0173.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "asd-1-0173.py"]
