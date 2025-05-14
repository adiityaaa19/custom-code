FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-2001b0c7da.py Tavily-2001b0c7da.py
COPY .env .env
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-2001b0c7da.py"]