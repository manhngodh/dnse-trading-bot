#!/bin/bash
echo "Stopping existing containers..."
docker compose -f docker-compose.dev.yml down

echo "Rebuilding and starting containers..."
docker compose -f docker-compose.dev.yml up --build -d

echo "Development environment restarted!"
echo "Frontend available at: http://localhost:3000"
echo "Backend available at: http://localhost:5501/api"
