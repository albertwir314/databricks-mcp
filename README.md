# Databricks MCP Server

A comprehensive Model Context Protocol (MCP) server that provides seamless integration between Claude AI and Databricks workspaces. This server enables natural language interaction with Databricks resources including notebooks, clusters, tables, and SQL warehouses across multiple workspace connections.

**🐳 Docker-based for complete cross-platform compatibility!** Works identically on Windows, WSL, Linux, and macOS.

## 🚀 Quick Start

### Prerequisites
- **Docker** installed ([Get Docker](https://docs.docker.com/get-docker/))
- **Databricks workspace** access with personal access tokens
- **Git** for cloning the repository

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd databricks-mcp

# Create your credentials file
cp databricks_connections_example.json databricks_connections.json
# Edit databricks_connections.json with your Databricks host and token

# Build the Docker image
docker build -t databricks-mcp:latest .

# Test the server
docker run --rm -i \
  -v $(pwd)/databricks_connections.json:/app/databricks_connections.json:ro \
  databricks-mcp:latest
```

**Windows PowerShell**: Replace `$(pwd)` with `${PWD}`
**Windows Git Bash**: Use `$(pwd)` as shown above

## 📋 Features

### Core Capabilities
- **Multi-workspace support**: Connect to multiple Databricks workspaces simultaneously
- **Notebook management**: Create, list, and read notebooks with natural language
- **Cluster operations**: Monitor and manage compute clusters
- **Data exploration**: Browse catalogs, schemas, and tables intuitively
- **SQL execution**: Run queries on SQL warehouses with automatic warehouse selection
- **Table introspection**: Get detailed schema and metadata information

### Architecture
- **FastMCP framework**: High-performance MCP server implementation
- **Databricks SDK**: Official SDK for robust workspace integration
- **Docker containerization**: Complete cross-platform compatibility
- **Zero dependencies**: No Python, pip, or UV installation required on host

## ⚙️ Configuration

### Databricks Credentials Setup

Create a `databricks_connections.json` file in the project root with your workspace credentials:

```json
{
  "connections": {
    "default": {
      "name": "default",
      "host": "https://your-workspace.azuredatabricks.net/",
      "token": "dapi1234567890abcdef"
    },
    "staging": {
      "name": "staging",
      "host": "https://staging-workspace.azuredatabricks.net/",
      "token": "dapi0987654321fedcba"
    }
  }
}
```

**Note**: This file is automatically ignored by git (see `.gitignore`). Never commit credentials to version control.

## 🛠️ Configuration

### Claude Desktop Setup

1. **Locate your Claude Desktop config file:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add this configuration:**

```json
{
  "mcpServers": {
    "databricks": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/absolute/path/to/databricks-mcp/databricks_connections.json:/app/databricks_connections.json:ro",
        "databricks-mcp:latest"
      ]
    }
  }
}
```

3. **Update the volume path:**
   - **Windows**: `C:\\Users\\YourName\\path\\to\\databricks-mcp\\databricks_connections.json:/app/databricks_connections.json:ro`
   - **macOS**: `/Users/yourname/path/to/databricks-mcp/databricks_connections.json:/app/databricks_connections.json:ro`
   - **Linux/WSL**: `/home/yourname/path/to/databricks-mcp/databricks_connections.json:/app/databricks_connections.json:ro`

4. **Restart Claude Desktop** and verify in Settings → Developer → MCP Servers

### Claude Code CLI Setup

**Option 1: Automated Registration (Recommended)**

```bash
# Run the registration script (builds image and registers globally)
./register-mcp-claude-code.sh
```

This registers the server at user scope, making it available across all Claude Code projects.

**Option 2: Manual Registration**

```bash
# Build the Docker image
docker build -t databricks-mcp:latest .

# Register with Claude Code CLI
claude mcp add -s user databricks \
  docker run --rm -i \
  -v /absolute/path/to/databricks-mcp/databricks_connections.json:/app/databricks_connections.json:ro \
  databricks-mcp:latest
```

**Option 3: Project-Specific Setup**

Create or edit `.mcp.json` in your project directory:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/absolute/path/to/databricks-mcp/databricks_connections.json:/app/databricks_connections.json:ro",
        "databricks-mcp:latest"
      ]
    }
  }
}
```

Replace `/absolute/path/to/databricks-mcp/` with:
- **Windows (WSL)**: `/mnt/c/Users/YourName/path/to/databricks-mcp/`
- **Linux**: `/home/yourname/path/to/databricks-mcp/`
- **macOS**: `/Users/yourname/path/to/databricks-mcp/`

## 🔧 Available Tools

### Connection Management
- `list_databricks_connections()`: List all configured workspace connections
- `add_databricks_connection(name, host, token)`: Add a new workspace connection at runtime

### Notebook Operations
- `create_notebook(path, language, content, connection_name)`: Create new notebooks (Python, SQL, Scala, R)
- `list_notebooks(path, connection_name)`: Browse workspace directories and notebooks
- `get_notebook_content(path, connection_name)`: Read notebook source code

### Cluster Management
- `list_clusters(connection_name)`: View all clusters with status, configuration, and worker counts

### Data Catalog Operations
- `list_catalogs(connection_name)`: Browse all available Unity Catalog instances
- `list_schemas(catalog_name, connection_name)`: Explore schemas within catalogs
- `list_tables(catalog_name, schema_name, connection_name)`: View tables within schemas
- `get_table_info(table_name, catalog_name, schema_name, connection_name)`: Get detailed table metadata including columns, types, and comments

### SQL Execution
- `execute_sql_query(query, warehouse_id, connection_name)`: Run SQL queries with automatic warehouse selection and result formatting
- `list_sql_warehouses(connection_name)`: View available SQL compute resources

## 💬 Usage Examples

### Creating Notebooks
```
Claude, create a Python notebook at '/Users/myname/data_analysis.py' with some basic pandas data exploration code for analyzing customer data.
```

### Data Exploration  
```
Claude, show me all the catalogs available, then list the tables in the 'sales' schema of the 'production' catalog, and describe the structure of the 'customers' table.
```

### SQL Queries
```
Claude, run a query to get the top 10 customers by total purchase amount from the sales.customers table, and show me which SQL warehouse was used.
```

### Multi-Workspace Operations
```
Claude, add a connection to our staging environment at 'https://staging.azuredatabricks.net/' called 'staging', then compare the table schemas between production and staging for the users table.
```

### Cluster Monitoring
```
Claude, show me the status of all clusters and identify any that are currently running but might be idle.
```

## 🐛 Troubleshooting

### Docker Issues

**Problem**: "Docker not found" or "command not found: docker"
- **Solution**: Install Docker Desktop:
  - **Windows/macOS**: [Docker Desktop](https://docs.docker.com/desktop/)
  - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Verify**: `docker --version`

**Problem**: "Cannot connect to Docker daemon"
- **Windows/macOS**: Launch Docker Desktop application
- **Linux**: `sudo systemctl start docker`

**Problem**: "Permission denied" on Linux
- **Solution**: Add user to docker group:
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  ```

**Problem**: Build fails
- **Check**: Internet connection
- **Try**: `docker pull python:3.11-slim` to pre-pull base image

### Configuration Issues

**Problem**: "Server disconnected" or "Connection failed"
- **Check**: Docker image exists: `docker images | grep databricks-mcp`
- **Rebuild**: `docker build -t databricks-mcp:latest .`
- **Verify**: Absolute path to `databricks_connections.json` in config

**Problem**: Volume mount errors on Windows
- **Use**: Double backslashes in JSON: `C:\\Users\\Name\\...`
- **Or**: Forward slashes: `C:/Users/Name/...`

**Problem**: "File not found" for databricks_connections.json
- **Check**: File exists: `ls databricks_connections.json`
- **Verify**: Using absolute path in configuration
- **Note**: Relative paths don't work with Docker volumes

### Claude Code CLI Issues

**Problem**: Registration script fails
- **Solution**: `chmod +x register-mcp-claude-code.sh`
- **Check**: Docker is running
- **Alternative**: Use manual registration

**Problem**: Server not in `claude mcp list`
- **Solution**: Re-run `./register-mcp-claude-code.sh`
- **Check**: `claude mcp list -s user`
- **Clean**: `claude mcp remove -s user databricks`

### Authentication Issues

**Problem**: "Invalid credentials"
- **Check**: `databricks_connections.json` exists and is mounted correctly
- **Verify**: Host URL format: `https://workspace.azuredatabricks.net/`
- **Test**: Token hasn't expired
- **Debug**: Run container directly:
  ```bash
  docker run --rm -i \
    -v $(pwd)/databricks_connections.json:/app/databricks_connections.json:ro \
    databricks-mcp:latest
  ```

### General Issues

**Problem**: Code changes not reflected
- **Solution**: Rebuild image after changes:
  ```bash
  docker build -t databricks-mcp:latest .
  ```
- **Clean build**: `docker build --no-cache -t databricks-mcp:latest .`

**Problem**: Multiple server instances
- **Solution**: Use unique names: `databricks-prod`, `databricks-staging`
- **Check**: Claude Desktop settings or `claude mcp list`

## 🔒 Security Best Practices

### Credential Management
- **Never commit** tokens to version control
- **Use environment variables** for sensitive data
- **Rotate tokens regularly** following your organization's security policy
- **Consider service principals** for production deployments

### Access Control
- **Principle of least privilege**: Grant minimum necessary permissions
- **Separate environments**: Use different tokens for dev/staging/prod
- **Monitor usage**: Review MCP server access logs regularly

### Configuration Security
- **Restrict file permissions** on configuration files containing tokens
- **Use workspace-scoped tokens** when possible
- **Implement token expiration** policies

## 📁 Project Structure

```
databricks-mcp/
├── src/
│   └── databricks_mcp/
│       ├── __init__.py
│       └── server.py                      # Main MCP server implementation
├── Dockerfile                             # Docker container definition
├── docker-compose.yml                     # Docker Compose configuration
├── .mcp.json                              # Your Claude Code CLI config
├── .mcp_example.json                      # Project-local config example
├── claude_desktop_config.json             # Your Claude Desktop config
├── claude_desktop_config_example.json     # Claude Desktop config example
├── databricks_connections.json            # Your credentials (gitignored)
├── databricks_connections_example.json    # Credentials template
├── register-mcp-claude-code.sh            # Automated registration script
├── pyproject.toml                         # Python dependencies
└── README.md                              # This file
```

### Key Components

- **Dockerfile**: Optimized single-stage build using pip
- **docker-compose.yml**: Optional simplified Docker setup
- **server.py**: FastMCP-based server with 12 Databricks integration tools
- **register-mcp-claude-code.sh**: Automated Docker build and registration
- **databricks_connections.json**: Your credentials (gitignored - see example)

## 🚀 Development

### Local Development Setup

For iterative development, mount your source code:
```bash
docker run --rm -it \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/databricks_connections.json:/app/databricks_connections.json:ro \
  databricks-mcp:latest
```

### Adding New Tools

1. Edit `src/databricks_mcp/server.py`
2. Add new `@mcp.tool()` decorated functions
3. Rebuild: `docker build -t databricks-mcp:latest .`
4. Test with Claude

### Adding Dependencies

1. Edit `pyproject.toml` dependencies section
2. Rebuild: `docker build -t databricks-mcp:latest .`

### Running Tests

```bash
docker run --rm -it databricks-mcp:latest pytest tests/
```

### Code Quality

```bash
# Format code
docker run --rm -it -v $(pwd):/app databricks-mcp:latest black src/

# Lint
docker run --rm -it -v $(pwd):/app databricks-mcp:latest ruff check src/

# Type check
docker run --rm -it -v $(pwd):/app databricks-mcp:latest mypy src/
```

### Using Docker Compose

```bash
# Start service
docker-compose up

# Run tests
docker-compose exec databricks-mcp pytest

# Stop service
docker-compose down
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## 📚 Additional Resources

- [Databricks SDK Documentation](https://databricks-sdk-py.readthedocs.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [UV Package Manager](https://docs.astral.sh/uv/)
- [Claude Code CLI Documentation](https://docs.anthropic.com/en/docs/claude-code)