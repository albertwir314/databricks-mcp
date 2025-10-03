# Dockerfile for Databricks MCP Server
# Provides cross-platform compatibility (Windows/WSL/Linux/macOS)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install package with dependencies
RUN pip install --no-cache-dir -e .

# Set Python path
ENV PYTHONPATH=/app/src

# Run the MCP server
# MCP uses stdio for communication, so no need to expose ports
CMD ["python", "-m", "databricks_mcp.server"]
