FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY soql123-fed0a8a4a9.py soql123-fed0a8a4a9.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "soql123-fed0a8a4a9.py"]