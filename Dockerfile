# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    chromium \
    chromium-driver \
    && apt-get clean

# Copy bot files
COPY . .

# Run bot
CMD ["python", "main.py"]
