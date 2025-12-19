.PHONY: build up down logs lint test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

lint:
	# Python linting
	pip install ruff
	ruff check .
	ruff format --check .
	# Frontend linting
	cd frontend && npm run lint

format:
	ruff format .
	cd frontend && npm run lint -- --fix

test:
	# Run backend tests (requires local env setup or docker run)
	docker-compose run --rm backend pytest
	
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
