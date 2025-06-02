FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-3eb79e17c9.py 
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-3eb79e17c9.py"]