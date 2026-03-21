# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV NODE_MAJOR=20
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install NodeJS
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get install -y nodejs

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Final cleanup of any potential leftover build files
RUN rm -rf .web

# Initialize the Reflex project
RUN reflex init

# Link the assets directory to the frontend's public folder
RUN rm -rf .web/public && ln -s /app/assets /app/.web/public

# Expose the ports for the frontend (3003) and backend (8003)
EXPOSE 3003 8003

# Comando para arrancar, asegurando migración de DB primero
CMD ["sh", "-c", "reflex db migrate && reflex run --env prod --frontend-port 3003 --backend-port 8003"]
