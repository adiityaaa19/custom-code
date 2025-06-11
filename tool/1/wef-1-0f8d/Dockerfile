FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY wef-1-0f8d.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "wef-1-0f8d.py"]
