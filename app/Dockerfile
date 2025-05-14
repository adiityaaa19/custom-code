FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY Tavily-509aa186d5.py Tavily-509aa186d5.py
COPY .env .env
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "Tavily-509aa186d5.py"]