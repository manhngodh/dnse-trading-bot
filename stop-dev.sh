#!/bin/bash
# filepath: /Users/manhngodh/development/trading/dnse-trading-bot/stop-dev.sh

echo "Stopping development environment..."

# Stop the development containers
docker compose -f docker-compose.dev.yml down

echo "Development environment stopped!"
