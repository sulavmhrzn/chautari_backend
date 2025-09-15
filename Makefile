.DEFAULT_GOAL := help
.PHONY: help run makemigrations migrate shell test clean install lint format check

# Django Commands
run:  ## Start the development server
	uv run manage.py runserver

makemigrations:  ## Create new database migrations
	uv run manage.py makemigrations

migrate:  ## Apply database migrations
	uv run manage.py migrate

shell:  ## Start Django shell
	uv run manage.py shell

# Development Commands
install:  ## Install dependencies
	uv sync

test:  ## Run tests
	uv run manage.py test

lint:  ## Run linting (if you use flake8/ruff)
	uv run ruff check .

format:  ## Format code (if you use black/ruff)
	uv run ruff format .

check: lint test  ## Run all checks (lint + test)

help:  ## Show this help message
	@echo "Available commands:"
	@echo ""
	@echo "Django Commands:"
	@echo "  run              Start the development server"
	@echo "  makemigrations   Create new database migrations"
	@echo "  migrate          Apply database migrations"
	@echo "  shell            Start Django shell"
	@echo ""
	@echo "Development Commands:"
	@echo "  install          Install dependencies"
	@echo "  test             Run tests"
	@echo "  lint             Run linting"
	@echo "  format           Format code"
	@echo "  check            Run all checks (lint + test)"
	@echo ""
	@echo "Utility Commands:"
	@echo "  help             Show this help message"