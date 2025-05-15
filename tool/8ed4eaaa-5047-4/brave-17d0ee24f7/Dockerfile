FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY brave-17d0ee24f7.py brave-17d0ee24f7.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "brave-17d0ee24f7.py"]