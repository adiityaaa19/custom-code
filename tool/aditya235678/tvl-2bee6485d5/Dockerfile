FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tvl-2bee6485d5.py tvl-2bee6485d5.py
COPY .env .env
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tvl-2bee6485d5.py"]