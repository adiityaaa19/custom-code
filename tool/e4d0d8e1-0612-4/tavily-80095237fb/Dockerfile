FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tavily-80095237fb.py tavily-80095237fb.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavily-80095237fb.py"]