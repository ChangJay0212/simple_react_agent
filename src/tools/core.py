"""
Tools module for the simple agent.
Provides various utility functions that can be used by the agent.
"""
from datetime import datetime
from typing import Dict, Any, List
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Abstract base class for all tools used by the agent.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the description of the tool for LLM to understand when to use it."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Return the parameters schema for the tool."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters and return the result."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class GetCurrentTimeTool(BaseTool):
    """
    Tool to get the current date and time information.
    Can provide time in different formats and timezones.
    """
    
    @property
    def name(self) -> str:
        return "get_current_time"
    
    @property
    def description(self) -> str:
        return (
            "Get the current date and time. Can return time in different formats. "
            "Use this tool when the user asks about current time, date, or when you need "
            "to provide timestamp information."
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "The format for the time output",
                    "enum": ["iso", "readable", "timestamp", "date_only", "time_only"],
                    "default": "readable"
                },
                "timezone": {
                    "type": "string", 
                    "description": "Timezone for the output (e.g., 'UTC', 'Asia/Taipei')",
                    "default": "local"
                }
            },
            "required": []
        }
    
    def execute(self, format: str = "readable", timezone: str = "local") -> str:
        """
        Execute the get current time tool.
        
        Args:
            format (str): Format of the time output
            timezone (str): Timezone for the output
            
        Returns:
            str: Current time in the specified format
        """
        try:
            now = datetime.now()
            
            if format == "iso":
                return now.isoformat()
            elif format == "timestamp":
                return str(int(now.timestamp()))
            elif format == "date_only":
                return now.strftime("%Y-%m-%d")
            elif format == "time_only":
                return now.strftime("%H:%M:%S")
            else:  # readable format (default)
                return now.strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception as e:
            return f"Error getting current time: {str(e)}"


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