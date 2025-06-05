FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tavily-3-b4491.py ./main.py
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "main.py"]
