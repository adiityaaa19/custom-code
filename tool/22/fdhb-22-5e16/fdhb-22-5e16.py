from fastmcp import FastMCP
import signal
from fastapi.middleware.cors import CORSMiddleware

mcp = FastMCP(
    name="fdhbrth",
    host='0.0.0.0',
    port=8000,
    debug=True
)

# Signal handler for graceful shutdown
def signal_handler(signal, frame):
    mcp.stop()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

from app.services.tool_registry import get_tools as get_tools_registry
from app.services.framework_registry import get_frameworks as get_frameworks_registry, get_framework_creds_schema
from fastapi import APIRouter

## API ENDPOINTS 
from app.api import agent as agent_router
from app.api import agent_lifecycle as agent_lifecycle_router

@mcp.tool()
def get_tools():
    return {"tools": get_tools_registry()}

@mcp.tool()
def get_frameworks():
    return {"frameworks": get_frameworks_registry()}

@mcp.tool()
def get_creds_schema(framework_name: str):
    return get_framework_creds_schema(framework_name)

if __name__ == "__main__":
    mcp.run(transport="http", path="/mcp")