FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-8127ce1147.py 
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-8127ce1147.py"]