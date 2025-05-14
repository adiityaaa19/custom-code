FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tavilyad23-a9dc4b4b99.py tavilyad23-a9dc4b4b99.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavilyad23-a9dc4b4b99.py"]