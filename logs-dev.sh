#!/bin/bash
# filepath: /Users/manhngodh/development/trading/dnse-trading-bot/logs-dev.sh

echo "Showing logs from development environment..."

# Show logs from the development containers
# Use CTRL+C to exit log view
docker compose  -f docker-compose.dev.yml logs -f $1

# Note: You can pass a service name as an argument to see only logs from that service
# Example: ./logs-dev.sh backend
