#!/bin/bash
# filepath: /Users/manhngodh/development/trading/dnse-trading-bot/dev.sh

echo "Starting development environment..."

# Build and start the development containers
docker compose -f docker-compose.dev.yml up -d --build

echo "Development environment started!"
echo "Backend API available at: http://localhost:5501"
echo "Frontend available at: http://localhost:80"
echo ""
echo "To view logs: docker compose -f docker-compose.dev.yml logs -f"
echo "To stop: docker compose -f docker-compose.dev.yml down"
