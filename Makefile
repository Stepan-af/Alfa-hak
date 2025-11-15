.PHONY: build up down logs test seed clean install-backend install-frontend

# Build all containers
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run tests
test:
	docker-compose exec api pytest
	cd frontend && npm run test

# Seed database with sample data
seed:
	docker-compose exec api python -m app.scripts.seed

# Clean everything (containers, volumes, images)
clean:
	docker-compose down -v
	docker system prune -af

# Install backend dependencies
install-backend:
	cd backend && pip install -r requirements.txt

# Install frontend dependencies
install-frontend:
	cd frontend && npm install

# Run backend locally (development)
dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally (development)
dev-frontend:
	cd frontend && npm run dev

# Run migrations
migrate:
	docker-compose exec api alembic upgrade head

# Test email configuration
test-email:
	@echo "📧 Testing email configuration..."
	docker-compose exec api python test_email.py

# Quick setup for first time
setup:
	@echo "🚀 Setting up Alfa Copilot..."
	docker-compose build
	docker-compose up -d
	@sleep 10
	docker-compose exec api alembic upgrade head
	@echo "✅ Setup complete! Access at http://localhost:3000"

# Create new migration
migration:
	docker-compose exec api alembic revision --autogenerate -m "$(name)"

# Setup everything from scratch
setup: build up migrate seed
	@echo "✅ Setup complete! Visit http://localhost:3000"
