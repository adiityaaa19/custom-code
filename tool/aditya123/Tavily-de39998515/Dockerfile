FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-de39998515.py Tavily-de39998515.py
COPY .env .env
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-de39998515.py"]