"""Databricks MCP Server implementation."""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Union
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import Language, ImportFormat
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


class DatabricksConnection(BaseModel):
    """Configuration for a Databricks connection."""
    name: str
    host: str
    token: str
    
    def create_client(self) -> WorkspaceClient:
        """Create a Databricks workspace client."""
        return WorkspaceClient(host=self.host, token=self.token)


class DatabricksManager:
    """Manages multiple Databricks connections."""
    
    def __init__(self):
        self.connections: Dict[str, DatabricksConnection] = {}
        self._load_connections()
    
    def _load_connections(self):
        """Load connections from config file, then environment variables."""
        # First try to load from config file
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "databricks_connections.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    for conn_name, conn_data in config.get("connections", {}).items():
                        self.connections[conn_name] = DatabricksConnection(
                            name=conn_data["name"],
                            host=conn_data["host"],
                            token=conn_data["token"]
                        )
            except Exception as e:
                print(f"Warning: Failed to load connections from config file: {e}")
        
        # Fallback to environment variables if no connections loaded
        if not self.connections:
            host = os.getenv("DATABRICKS_HOST")
            token = os.getenv("DATABRICKS_TOKEN")
            
            if host and token:
                self.connections["default"] = DatabricksConnection(
                    name="default",
                    host=host,
                    token=token
                )
    
    def add_connection(self, name: str, host: str, token: str):
        """Add a new Databricks connection."""
        self.connections[name] = DatabricksConnection(
            name=name, host=host, token=token
        )
    
    def get_client(self, connection_name: str = "default") -> WorkspaceClient:
        """Get a Databricks client for the specified connection."""
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        return self.connections[connection_name].create_client()
    
    def list_connections(self) -> List[str]:
        """List available connection names."""
        return list(self.connections.keys())


# Initialize the FastMCP server and Databricks manager
mcp = FastMCP("Databricks MCP Server")
databricks_manager = DatabricksManager()


@mcp.tool()
def list_databricks_connections(connection_name: str = "default") -> Dict[str, Any]:
    """List all available Databricks connections.
    
    Args:
        connection_name: Parameter ignored but required for Claude Code compatibility
    """
    connections = databricks_manager.list_connections()
    return {"connections": connections}


@mcp.tool()
def add_databricks_connection(name: str, host: str, token: str) -> str:
    """Add a new Databricks connection.
    
    Args:
        name: Name for the connection
        host: Databricks workspace URL
        token: Databricks access token
    """
    databricks_manager.add_connection(name, host, token)
    return f"Connection '{name}' added successfully"


@mcp.tool()
def list_clusters(connection_name: str = "default") -> List[Dict[str, Any]]:
    """List all clusters in the Databricks workspace.
    
    Args:
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    clusters = []
    
    for cluster in client.clusters.list():
        clusters.append({
            "cluster_id": cluster.cluster_id,
            "cluster_name": cluster.cluster_name,
            "state": cluster.state.value if cluster.state else None,
            "node_type_id": cluster.node_type_id,
            "num_workers": cluster.num_workers
        })
    
    return clusters


@mcp.tool()
def create_notebook(
    path: str,
    language: str = "PYTHON",
    content: str = "",
    connection_name: str = "default"
) -> str:
    """Create a new notebook in Databricks workspace.
    
    Args:
        path: Path where to create the notebook
        language: Programming language (PYTHON, SQL, SCALA, R)
        content: Initial content for the notebook
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    
    # Map string to Language enum
    lang_map = {
        "PYTHON": Language.PYTHON,
        "SQL": Language.SQL, 
        "SCALA": Language.SCALA,
        "R": Language.R
    }
    
    if language.upper() not in lang_map:
        raise ValueError(f"Unsupported language: {language}")
    
    client.workspace.upload(
        path=path,
        format=ImportFormat.SOURCE,
        language=lang_map[language.upper()],
        content=content.encode("utf-8") if content else b"",
        overwrite=True
    )
    
    return f"Notebook created at {path}"


@mcp.tool()
def list_notebooks(path: str = "/", connection_name: str = "default") -> List[Dict[str, Any]]:
    """List notebooks and folders in the workspace.
    
    Args:
        path: Path to list (defaults to root)
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    items = []
    
    try:
        for item in client.workspace.list(path):
            items.append({
                "path": item.path,
                "object_type": item.object_type.value if item.object_type else None,
                "language": item.language.value if item.language else None,
                "size": item.size
            })
    except Exception as e:
        return [{"error": str(e)}]
    
    return items


@mcp.tool()
def get_notebook_content(path: str, connection_name: str = "default") -> str:
    """Get the content of a notebook.
    
    Args:
        path: Path to the notebook
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    
    try:
        response = client.workspace.download(path)
        return response.decode("utf-8")
    except Exception as e:
        return f"Error reading notebook: {str(e)}"


@mcp.tool()
def execute_sql_query(
    query: str,
    warehouse_id: Optional[str] = None,
    connection_name: str = "default"
) -> Dict[str, Any]:
    """Execute a SQL query on Databricks SQL warehouse.
    
    Args:
        query: SQL query to execute
        warehouse_id: SQL warehouse ID (optional)
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    
    try:
        # If no warehouse_id provided, try to get the first available one
        if not warehouse_id:
            warehouses = list(client.warehouses.list())
            if not warehouses:
                return {"error": "No SQL warehouses available"}
            warehouse_id = warehouses[0].id
        
        # Execute the query
        response = client.statement_execution.execute_statement(
            statement=query,
            warehouse_id=warehouse_id
        )
        
        return {
            "statement_id": response.statement_id,
            "status": response.status.state.value if response.status else None,
            "result": response.result.data_array if response.result else None,
            "schema": [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else None
        }
        
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_catalogs(connection_name: str = "default") -> List[Dict[str, Any]]:
    """List all catalogs in the Databricks workspace.
    
    Args:
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    catalogs = []
    
    try:
        for catalog in client.catalogs.list():
            catalogs.append({
                "name": catalog.name,
                "comment": catalog.comment,
                "full_name": catalog.full_name,
                "catalog_type": catalog.catalog_type.value if catalog.catalog_type else None
            })
    except Exception as e:
        return [{"error": str(e)}]
    
    return catalogs


@mcp.tool()
def list_schemas(
    catalog_name: str = "main",
    connection_name: str = "default"
) -> List[Dict[str, Any]]:
    """List schemas in a catalog.
    
    Args:
        catalog_name: Name of the catalog
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    schemas = []
    
    try:
        for schema in client.schemas.list(catalog_name=catalog_name):
            schemas.append({
                "name": schema.name,
                "catalog_name": schema.catalog_name,
                "comment": schema.comment,
                "full_name": schema.full_name
            })
    except Exception as e:
        return [{"error": str(e)}]
    
    return schemas


@mcp.tool()
def list_tables(
    catalog_name: str = "main",
    schema_name: str = "default", 
    connection_name: str = "default"
) -> List[Dict[str, Any]]:
    """List tables in a schema.
    
    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    tables = []
    
    try:
        for table in client.tables.list(catalog_name=catalog_name, schema_name=schema_name):
            tables.append({
                "name": table.name,
                "catalog_name": table.catalog_name,
                "schema_name": table.schema_name,
                "table_type": table.table_type.value if table.table_type else None,
                "comment": table.comment
            })
    except Exception as e:
        return [{"error": str(e)}]
    
    return tables


@mcp.tool()
def get_table_info(
    table_name: str,
    catalog_name: str = "main",
    schema_name: str = "default",
    connection_name: str = "default"
) -> Dict[str, Any]:
    """Get detailed information about a table.
    
    Args:
        table_name: Name of the table
        catalog_name: Name of the catalog
        schema_name: Name of the schema
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    
    try:
        table = client.tables.get(
            full_name=f"{catalog_name}.{schema_name}.{table_name}"
        )
        
        columns = []
        if table.columns:
            for col in table.columns:
                columns.append({
                    "name": col.name,
                    "type_name": col.type_name,
                    "type_text": col.type_text,
                    "comment": col.comment,
                    "nullable": col.nullable
                })
        
        return {
            "name": table.name,
            "catalog_name": table.catalog_name,
            "schema_name": table.schema_name,
            "table_type": table.table_type.value if table.table_type else None,
            "comment": table.comment,
            "columns": columns,
            "storage_location": table.storage_location,
            "data_source_format": table.data_source_format.value if table.data_source_format else None
        }
        
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_sql_warehouses(connection_name: str = "default") -> List[Dict[str, Any]]:
    """List SQL warehouses in the workspace.
    
    Args:
        connection_name: Name of the Databricks connection to use
    """
    client = databricks_manager.get_client(connection_name)
    warehouses = []
    
    try:
        for warehouse in client.warehouses.list():
            warehouses.append({
                "id": warehouse.id,
                "name": warehouse.name,
                "state": warehouse.state.value if warehouse.state else None,
                "cluster_size": warehouse.cluster_size,
                "num_clusters": warehouse.num_clusters
            })
    except Exception as e:
        return [{"error": str(e)}]
    
    return warehouses


def main():
    """Run the MCP server."""
    # FastMCP uses stdio transport by default
    mcp.run()


if __name__ == "__main__":
    main()