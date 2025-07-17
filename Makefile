# Makefile for twat-hatch development

.PHONY: help install test build release clean lint format type-check dev-setup

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in development mode
	pip install -e .

dev-setup:  ## Set up development environment
	./scripts/dev-setup.sh

test:  ## Run tests
	./scripts/test.sh

build:  ## Build the package
	./scripts/build.sh

release:  ## Create a new release (usage: make release VERSION=1.2.3)
	./scripts/release.sh $(VERSION)

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".coverage" -delete
	find . -name "coverage.xml" -delete

lint:  ## Run linting
	hatch run lint:style

format:  ## Format code
	hatch run lint:fmt

type-check:  ## Run type checking
	hatch run lint:typing

coverage:  ## Run tests with coverage
	hatch run test-cov

security:  ## Run security checks
	bandit -r src/
	safety check

pre-commit:  ## Run pre-commit hooks
	pre-commit run --all-files

ci:  ## Run all CI checks locally
	make lint
	make type-check
	make security
	make test

all: clean install test build  ## Run clean, install, test, and build