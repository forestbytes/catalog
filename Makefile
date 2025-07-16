.PHONY: up down build logs clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  up      - Start all services with docker compose"
	@echo "  down    - Stop all services"
	@echo "  build   - Build and start services"
	@echo "  logs    - Show logs from all services"
	@echo "  clean   - Stop services and remove volumes"
	@echo "  help    - Show this help message"

# Start services
up:
	cd docker && docker compose up -d

# Stop services
down:
	cd docker && docker compose down

# Build and start services
build:
	cd docker && docker compose up -d --build --remove-orphans

# Show logs
logs:
	cd docker && docker compose logs -f

# Clean up (stop services and remove volumes)
clean:
	cd docker && docker compose down -v

# Start services in foreground (useful for development)
up-fg:
	cd docker && docker compose up
