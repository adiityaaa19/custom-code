FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY addtool-87f480aac3.py addtool-87f480aac3.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "addtool-87f480aac3.py"]