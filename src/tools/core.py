"""
Tools module for the simple agent.
Provides various utility functions that can be used by the agent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


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
            "parameters": self.parameters,
        }
