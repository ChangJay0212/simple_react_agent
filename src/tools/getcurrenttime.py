from datetime import datetime
from typing import Any, Dict

from tools.core import BaseTool


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
                    "default": "readable",
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone for the output (e.g., 'UTC', 'Asia/Taipei')",
                    "default": "local",
                },
            },
            "required": [],
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
