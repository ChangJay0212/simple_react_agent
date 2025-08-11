from typing import Any, Dict, List

from tools.core import BaseTool
from tools.getcurrenttime import GetCurrentTimeTool


class ToolManager:
    """
    Manager class to handle all available tools for the agent.
    """

    def __init__(self):
        """Initialize the tool manager with available tools."""
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register all default tools."""
        self.register_tool(GetCurrentTimeTool())

    def register_tool(self, tool: BaseTool):
        """
        Register a new tool.

        Args:
            tool (BaseTool): The tool to register
        """
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """
        Get a tool by name.

        Args:
            name (str): The name of the tool

        Returns:
            BaseTool: The requested tool

        Raises:
            KeyError: If the tool is not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found")
        return self.tools[name]

    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> str:
        """
        Execute a tool with given parameters.

        Args:
            name (str): The name of the tool to execute
            parameters (Dict[str, Any]): Parameters for the tool

        Returns:
            str: Result of the tool execution
        """
        try:
            tool = self.get_tool(name)
            return tool.execute(**parameters)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools in dictionary format for LLM function calling.

        Returns:
            List[Dict[str, Any]]: List of tool descriptions
        """
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool_names(self) -> List[str]:
        """
        Get all available tool names.

        Returns:
            List[str]: List of tool names
        """
        return list(self.tools.keys())
