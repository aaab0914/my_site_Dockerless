# Dockerfile
# Use the official Python image.
FROM python:3.12-slim

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory.
WORKDIR /app

# Install system dependencies when needed.
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file.
COPY requirements.txt /app/

# Install Python dependencies.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the project files.
COPY . /app/

# Collect static files.
# RUN python manage.py collectstatic --noinput

# Expose the application port.
EXPOSE 8000

# Start the application.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
