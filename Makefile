.PHONY: build up down logs lint test clean format

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

lint:
	# Python linting
	ruff check .
	ruff format --check .
	# Frontend linting
	cd frontend && npm run lint

format:
	ruff format .
	ruff check --fix .
	cd frontend && npm run lint -- --fix

test:
	# Run backend tests
	docker compose run --rm backend pytest
	
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
