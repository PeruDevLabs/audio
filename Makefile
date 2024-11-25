# Variables
SERVICE_NAME=audio
DOCKER_COMPOSE=docker-compose
DOCKER_BUILD=docker build

# Default target
.DEFAULT_GOAL := help

# Help Function
.PHONY: help
help: ## Display this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Docker Commands
.PHONY: build
build: ## Build the audio Docker image
	$(DOCKER_BUILD) -t $(SERVICE_NAME) .

.PHONY: up
up: ## Start the audio service
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down: ## Stop the audio service
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs: ## Show logs from the audio service
	$(DOCKER_COMPOSE) logs -f $(SERVICE_NAME)

# Clean
.PHONY: clean
clean: ## Clean up temporary files and Docker containers
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
	find . -type f -name "*.pyo" -exec rm -f {} +
	$(DOCKER_COMPOSE) down --volumes --remove-orphans