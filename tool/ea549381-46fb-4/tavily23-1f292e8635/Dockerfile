FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tavily23-1f292e8635.py tavily23-1f292e8635.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavily23-1f292e8635.py"]