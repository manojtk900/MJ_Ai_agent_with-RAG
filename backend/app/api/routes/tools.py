"""
Tools API Route — MCP tool discovery and invocation.
"""
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/tools")


class ToolCallRequest(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]
    user_id: str = "anonymous"


@router.get("/")
async def list_tools():
    """List all available MCP tools."""
    try:
        from app.core.mcp.registry import tool_registry
        tools = tool_registry.list_all()
        return {
            "tools": [t.to_mcp_schema() for t in tools],
            "count": len(tools),
        }
    except Exception as e:
        return {
            "tools": [],
            "count": 0,
            "message": f"Tool registry not fully initialized: {str(e)}",
        }


@router.get("/manifest")
async def get_mcp_manifest():
    """Get the full MCP manifest for tool discovery."""
    try:
        from app.core.mcp.gateway import mcp_gateway
        return mcp_gateway.get_mcp_manifest()
    except Exception as e:
        return {
            "schema_version": "0.1",
            "name": "mj-ai-assistant",
            "description": "MJ AI Assistant MCP Tool Server",
            "tools": [],
            "error": str(e),
        }


@router.post("/{tool_name}/call")
async def call_tool(tool_name: str, request: ToolCallRequest):
    """Invoke a specific MCP tool directly."""
    try:
        from app.core.mcp.gateway import mcp_gateway
        result = await mcp_gateway.call_tool(
            tool_name=tool_name,
            tool_input=request.tool_input,
            user_id=request.user_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@router.get("/categories")
async def list_categories():
    """List tools grouped by category."""
    try:
        from app.core.mcp.registry import tool_registry
        categories: Dict[str, list] = {}
        for tool in tool_registry.list_all():
            cat = tool.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool.name)
        return categories
    except Exception as e:
        return {"error": str(e), "categories": {}}
