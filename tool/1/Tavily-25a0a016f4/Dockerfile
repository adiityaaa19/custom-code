FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-25a0a016f4.py 
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-25a0a016f4.py"]