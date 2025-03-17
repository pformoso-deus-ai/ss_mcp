.PHONY: install test format lint typecheck clean server client

# Default Python interpreter
PYTHON := python3

# Default port for the server
PORT := 8000

# Install dependencies
install:
	uv pip install -r requirements.txt

# Run tests
test:
	pytest tests/ -v --cov=.

# Format code
format:
	isort .
	ruff format .

# Lint code
lint:
	ruff check .
	isort --check .

# Type checking
typecheck:
	mypy --ignore-missing-imports .

# Clean up cache files
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -name "*.pyc" -delete

# Start the server
server:
	$(PYTHON) server.py

# Run the client
client:
	$(PYTHON) client.py $(ARGS)

# Run all checks
check: format lint typecheck test

# Help
help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies using uv"
	@echo "  test       - Run tests with pytest"
	@echo "  format     - Format code with isort and ruff"
	@echo "  lint       - Lint code with ruff and isort"
	@echo "  typecheck  - Type check code with mypy"
	@echo "  clean      - Clean up cache files"
	@echo "  server     - Start the MCP server"
	@echo "  client     - Run the MCP client (use ARGS='command args' to pass arguments)"
	@echo "  check      - Run all checks (format, lint, typecheck, test)"
	@echo "  help       - Show this help message" 