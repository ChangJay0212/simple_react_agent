import os
from typing import Any, Dict, Optional

import requests

from tools.core import BaseTool


class RecognizeFaceTool(BaseTool):
    """
    Call a local face recognition API with an image file and return a natural-language summary.
    """

    def __init__(self, api_url: Optional[str] = None, timeout: float = 15.0):
        self._api_url = api_url or os.getenv(
            "FACE_API_URL", "http://10.204.16.59:8000/recognize_face/"
        )
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "recognize_face"

    @property
    def description(self) -> str:
        return (
            "Upload an image to the face-recognition endpoint and return how many people are present "
            "and their names if recognized."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        # JSON Schema for function calling / tool invocation
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the image file to analyze.",
                },
            },
            "required": ["file_path"],
            "additionalProperties": False,
        }

    def execute(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(self._api_url, files=files)
        data = response.json()
        number_of_people = data["num"]
        names = data["names"]
        result = ""
        for name in names:
            result = result + name + ","
        if number_of_people == 1:
            result = "There is one person in the picture, his/her name is " + result
        elif number_of_people > 1:
            result = (
                "There are"
                + str(number_of_people)
                + "people in the picture, their names are "
                + result
            )
        else:
            result = "There is no person in the picture"
        return result
