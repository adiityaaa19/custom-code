FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tavily_web_search_-56-50f6c.py ./main.py
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "main.py"]
