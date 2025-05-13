FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY requirements.txt .
COPY main.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8001

# Ensure environment variables from .env are read at runtime
ENV PYTHONUNBUFFERED=1

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]