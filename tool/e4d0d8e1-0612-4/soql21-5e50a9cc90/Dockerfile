FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY soql21-5e50a9cc90.py soql21-5e50a9cc90.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "soql21-5e50a9cc90.py"]