FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY brave-45a2e7249e.py brave-45a2e7249e.py
COPY .env .env
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "brave-45a2e7249e.py"]