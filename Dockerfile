# Use the official minimal Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Disable Python .pyc bytecode files
ENV PYTHONDONTWRITEBYTECODE 1
# Force stdout/stderr to be unbuffered (immediate logging)
ENV PYTHONUNBUFFERED 1

# Install system dependencies:
# - gcc: for compiling Python packages with native extensions
# - libpq-dev: for PostgreSQL client development headers (used by psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Set the default command to start the Kafka consumer worker
CMD ["python", "main.py"]
