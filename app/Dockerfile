FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY main.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8080

# Copy .env file for production
COPY .env .env

# Set entrypoint
ENTRYPOINT ["python", "main.py"]
