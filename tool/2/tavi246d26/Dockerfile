FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tavily_web_app_2_0c759fb9.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavily_web_app_2_0c759fb9.py"]
