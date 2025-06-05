FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tavily_web_search_3_3429939d.py .
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tavily_web_search_3_3429939d.py"]
