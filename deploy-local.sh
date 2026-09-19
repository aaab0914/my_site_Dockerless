#!/bin/bash

echo "🚀 Starting local deployment..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "🧹 Stopping and removing old containers..."
docker compose down

echo "🔧 Building and starting containers..."
docker compose up -d --build

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "📦 Running migrations..."
docker exec my_site_web python manage.py migrate

echo "✅ Checking service status..."
if curl -s http://localhost:8001/ > /dev/null; then
    echo "✅ Deployment successful! Application running at http://localhost:8001/"
else
    echo "❌ Deployment failed. Please check logs."
    docker compose logs web
fi
