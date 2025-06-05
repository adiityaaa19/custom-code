FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY tool_tvily_2_91815e4a.py .
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "tool_tvily_2_91815e4a.py"]
