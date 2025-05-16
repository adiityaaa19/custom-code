FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY soql-add-481b82c779.py soql-add-481b82c779.py
COPY .env .env
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "soql-add-481b82c779.py"]