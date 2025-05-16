FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY soql123-39c6f5f65a.py soql123-39c6f5f65a.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "soql123-39c6f5f65a.py"]