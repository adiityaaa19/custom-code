```dockerfile
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy only necessary files
COPY main.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8001

# Ensure environment variables from .env are available at runtime
ENV PYTHONUNBUFFERED=1

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]
```