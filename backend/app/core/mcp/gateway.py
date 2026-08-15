"""
MCP Gateway — First-class MCP integration layer.
Routes tool calls to appropriate MCP servers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog
from app.core.mcp.registry import tool_registry

log = structlog.get_logger(__name__)


class MCPGateway:
    """
    Central gateway for all MCP tool invocations.
    
    Architecture:
        Controller Agent
               │
               ▼
          MCP Gateway  ←── This class
               │
        ┌──────┼──────────┐
        ▼      ▼          ▼
      GitHub  Browser  Filesystem
      Server  Server    Server
    """

    def __init__(self):
        self._servers: Dict[str, Any] = {}
        self._call_count: int = 0

    def register_server(self, name: str, server: Any) -> None:
        """Register an MCP server."""
        self._servers[name] = server
        log.info("MCP server registered", name=name)

    async def call_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route a tool call through the MCP gateway.
        Handles logging, error recovery, and audit trail.
        """
        self._call_count += 1
        log.info("MCP tool call", tool=tool_name, call_id=self._call_count, user=user_id)

        try:
            result = await tool_registry.call(tool_name, tool_input)
            log.info("MCP tool success", tool=tool_name, call_id=self._call_count)
            return {"success": True, "result": result, "tool": tool_name}
        except ValueError as e:
            # Tool not found
            log.warning("MCP tool not found", tool=tool_name, error=str(e))
            return {"success": False, "error": f"Tool not found: {tool_name}", "available": self.list_tools()}
        except Exception as e:
            log.error("MCP tool error", tool=tool_name, error=str(e))
            return {"success": False, "error": str(e), "tool": tool_name}

    def list_tools(self) -> List[str]:
        """List all available tools."""
        return [t.name for t in tool_registry.list_all()]

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format."""
        return [t.to_openai_schema() for t in tool_registry.list_all()]

    def get_mcp_manifest(self) -> Dict[str, Any]:
        """Get full MCP manifest for tool discovery."""
        return {
            "schema_version": "0.1",
            "name": "mj-ai-assistant",
            "description": "MJ AI Assistant MCP Tool Server",
            "tools": [t.to_mcp_schema() for t in tool_registry.list_all()],
            "servers": list(self._servers.keys()),
        }


# Singleton gateway
mcp_gateway = MCPGateway()
