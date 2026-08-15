"""
MCP Tool Registry — Central registry for all Model Context Protocol tools.
Tools are registered here and dispatched through the MCP Gateway.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import structlog

log = structlog.get_logger(__name__)


class ToolDefinition:
    """Represents a single MCP-compatible tool."""

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: Dict[str, Any],
        requires_approval: bool = False,
        category: str = "general",
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters = parameters
        self.requires_approval = requires_approval
        self.category = category

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert to MCP tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {"type": "object", "properties": self.parameters},
        }


class ToolRegistry:
    """
    Central registry for all tools available to agents.
    Supports MCP protocol, LangChain tools, and custom handlers.
    """

    _instance: Optional["ToolRegistry"] = None

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, ToolDefinition] = {}
            cls._instance._initialized = False
        return cls._instance

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
        log.debug("Tool registered", name=tool.name, category=tool.category)

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_all(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def list_by_category(self, category: str) -> List[ToolDefinition]:
        return [t for t in self._tools.values() if t.category == category]

    async def call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool by name with given inputs."""
        tool = self.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registry. Available: {list(self._tools.keys())}")
        log.info("Tool invoked", name=tool_name, input_keys=list(tool_input.keys()))
        try:
            result = await tool.handler(**tool_input)
            return result
        except Exception as e:
            log.error("Tool error", name=tool_name, error=str(e))
            raise

    def initialize_default_tools(self) -> None:
        """Register all built-in tools."""
        if self._initialized:
            return
        self._register_web_tools()
        self._register_file_tools()
        self._register_memory_tools()
        self._register_system_tools()
        self._initialized = True
        log.info("Tool registry initialized", count=len(self._tools))

    def _register_web_tools(self) -> None:
        from app.core.mcp.servers.browser import navigate_url, extract_text

        self.register(ToolDefinition(
            name="web_search",
            description="Search the web for current information",
            handler=self._web_search_handler,
            parameters={"query": {"type": "string", "description": "Search query"}},
            category="search",
        ))
        self.register(ToolDefinition(
            name="browser_navigate",
            description="Navigate to a URL and extract content",
            handler=navigate_url,
            parameters={"url": {"type": "string", "description": "URL to navigate to"}},
            category="browser",
        ))

    def _register_file_tools(self) -> None:
        from app.core.mcp.servers.filesystem import read_file, write_file, list_directory

        self.register(ToolDefinition(
            name="file_read", description="Read file contents", handler=read_file,
            parameters={"path": {"type": "string"}}, category="filesystem",
        ))
        self.register(ToolDefinition(
            name="file_write", description="Write content to a file", handler=write_file,
            parameters={"path": {"type": "string"}, "content": {"type": "string"}},
            requires_approval=False, category="filesystem",
        ))
        self.register(ToolDefinition(
            name="dir_list", description="List directory contents", handler=list_directory,
            parameters={"path": {"type": "string"}}, category="filesystem",
        ))

    def _register_memory_tools(self) -> None:
        from app.core.memory.long_term import LongTermMemory
        lt = LongTermMemory()

        self.register(ToolDefinition(
            name="memory_store", description="Store information in long-term memory",
            handler=lt.store, parameters={"user_id": {"type": "string"}, "content": {"type": "string"}},
            category="memory",
        ))
        self.register(ToolDefinition(
            name="memory_search", description="Search long-term memory semantically",
            handler=lt.search, parameters={"user_id": {"type": "string"}, "query": {"type": "string"}},
            category="memory",
        ))

    def _register_system_tools(self) -> None:
        import subprocess
        async def run_cmd(command: str) -> str:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return r.stdout or r.stderr

        self.register(ToolDefinition(
            name="run_command", description="Execute a shell command",
            handler=run_cmd, parameters={"command": {"type": "string"}},
            requires_approval=True, category="system",
        ))

    @staticmethod
    async def _web_search_handler(query: str) -> str:
        from app.config import settings
        if settings.tavily_api_key:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.tavily_api_key)
            results = client.search(query, max_results=5)
            return str(results)
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return str(results)


# Singleton instance
tool_registry = ToolRegistry()
tool_registry.initialize_default_tools()
