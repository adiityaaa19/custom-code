FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tavily5643-f2bd9fe0fa.py tavily5643-f2bd9fe0fa.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavily5643-f2bd9fe0fa.py"]