#!/bin/bash

echo "🚀 Starting local deployment..."

# 1. Ensure Docker is running.
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# 2. Stop and remove old containers.
echo "🧹 Stopping and removing old containers..."
docker compose down

# 3. Rebuild and start the services.
echo "🔧 Building and starting containers..."
docker compose up -d --build

# 4. Wait for the database to become ready.
echo "⏳ Waiting for database to be ready..."
sleep 10

# 5. Run migrations.
echo "📦 Running migrations..."
docker exec my_site_web python manage.py migrate

# 6. Check service health.
echo "✅ Checking service status..."
if curl -s http://localhost:8001/ > /dev/null; then
    echo "✅ Deployment successful! Application running at http://localhost:8001/"
else
    echo "❌ Deployment failed. Please check logs."
    docker compose logs web
fi
