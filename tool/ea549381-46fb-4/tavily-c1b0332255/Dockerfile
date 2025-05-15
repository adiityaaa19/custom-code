FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tavily-c1b0332255.py tavily-c1b0332255.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavily-c1b0332255.py"]