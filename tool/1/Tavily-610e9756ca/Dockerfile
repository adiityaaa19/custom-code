FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-610e9756ca.py 
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-610e9756ca.py"]