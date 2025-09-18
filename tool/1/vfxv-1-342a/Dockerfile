FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY vfxv-1-342a.py .
COPY .env .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "vfxv-1-342a.py"]
