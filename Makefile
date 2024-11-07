# Configuration Variables
PORT=8000
APP=chat
VERSION=$(shell git describe --tags --always --dirty || echo "latest")
IMAGE_NAME=$(APP):$(VERSION)

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Default target: Show menu when no target is provided
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk '/^[a-zA-Z_-]+:/ {print "  " $$1}' $(MAKEFILE_LIST) | sed 's/://'
	@echo ""
	@echo "Examples:"
	@echo "  make dev        - Run development tasks (format, lint, test)"
	@echo "  make build      - Build the Docker image"
	@echo "  make test       - Run tests with coverage"
	@echo "  make deploy     - Deploy the service"
	@echo "  make monitor    - Run health checks and metrics monitoring"
	@echo ""


.PHONY: format
format:
	poetry run black .
	poetry run isort .

.PHONY: lint
lint:
	poetry run black .
	poetry run isort .

.PHONY: run-dev
dev:
	poetry run uvicorn main:app --reload --port $(PORT) --host 0.0.0.0

.PHONY: install
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install poetry
	poetry install
	poetry export --without-hashes --format=requirements.txt > requirements.txt

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .venv dist build *.egg-info
	rm -rf .pytest_cache .mypy_cache .coverage
	rm -f requirements.txt
	rm -r *.lock

.PHONY: test
test:
	poetry run pytest

.PHONY: build
build:
	docker build -t $(IMAGE_NAME) .

.PHONY: compose-up
compose-up:
	docker compose up -d --build

.PHONY: release
release:
	docker tag $(IMAGE_NAME) your-registry/$(IMAGE_NAME)
	docker push your-registry/$(IMAGE_NAME)

.PHONY: deploy
deploy: compose-down compose-up

.PHONY: compose-down
compose-down:
	docker compose down

.PHONY: deploy-clean
deploy-clean:
	docker compose down --volumes

.PHONY: ops
ops: status logs

.PHONY: status
status:
	docker ps | grep $(APP) || echo "Service not running."

.PHONY: logs
logs:
	docker compose logs -f

.PHONY: restart
restart:
	docker compose restart

.PHONY: monitor
monitor: health-check metrics

.PHONY: health-check
health-check:
	curl --fail http://localhost:$(PORT)/health || echo "Service is not healthy."

.PHONY: metrics
metrics:
	docker stats --no-stream $(shell docker ps -q --filter "name=$(APP)")

.PHONY: publish
publish:
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "Error: PYPI_TOKEN environment variable is not set"; \
		echo "Please set the PYPI_TOKEN environment variable with your PyPI API token"; \
		exit 1; \
	fi
	@echo "Building the package..."
	poetry build
	@echo "Publishing to PyPI..."
	poetry config pypi-token.pypi $$PYPI_TOKEN
	poetry publish
	@echo "Package published successfully!"
	@echo "Cleaning up..."
	poetry config --unset pypi-token.pypi


.PHONY: publish-test
publish-test:
	poetry publish --dry-run
	poetry config pypi-token.pypi $$PYPI_TOKEN
	poetry publish --dry-run
	@echo "Package published successfully!"
	@echo "Cleaning up..."
	poetry config --unset pypi-token.pypi