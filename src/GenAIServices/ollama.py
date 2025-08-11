import json
import time
from typing import Generator

import httpx

from GenAIServices.core import GenAIOperator


class OllamaHandler(GenAIOperator):
    def __init__(self, url: str):
        """Initializes the Ollama API client.
        Args:
            url (str): The base URL of the Ollama API.
        Raises:
            RuntimeError: If the connection to the Ollama API fails.

        """
        if not url.endswith("/"):
            url += "/"
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("URL must start with 'http://' or 'https://'")
        self.url = self._connect(url=url)

    def _connect(self, url: str) -> None:
        """Connects to the Ollama API.
        Args:
            url (str): The base URL of the Ollama API.
        Returns:
            str: The base URL of the Ollama API if the connection is successful.
        Raises:
            RuntimeError: If the connection fails.
        """
        try:
            response = httpx.get(url)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to connect to Ollama API: {response.status_code}"
                )
            return url
        except httpx.RequestError as e:
            raise RuntimeError(f"Connection error: {str(e)}")

    def _check_ollama_model_exists(self, url: str, model_name: str) -> bool:
        """Checks if a model exists in the Ollama API.

        Args:
            url (str): The base URL of the Ollama API.
            model_name (str): The name of the model to check.
        Returns:
            bool: True if the model exists, False otherwise.
        """
        try:
            response = httpx.get(url + "api/tags", timeout=5.0)
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(m["name"] == model_name for m in models)
        except httpx.RequestError as e:
            print(f" Request failed: {e}")
            return False
        except Exception as e:
            print(f" Unexpected error: {e}")
            return False

    def chat(self, request_data: dict) -> Generator[str, None, None]:
        """Generates a chat stream from the Ollama API.
        Args:
            request_data (dict): The request data to send to the API.
        Yields:
            str: The generated text from the API.
        Example:
            request_data = {
                "model": "llama3.2:1b",
                "messages": [{"role": "user", "content": "how r u?"}],
            }

        Raises:
            RuntimeError: If the response status code is not 200.
            json.JSONDecodeError: If the response cannot be decoded as JSON.
            BaseException: For any other exceptions that occur during the request.
        """
        headers = {"Content-Type": "application/json"}
        if not self._check_ollama_model_exists(
            url=self.url, model_name=request_data["model"]
        ):
            raise RuntimeError(
                f"Model {request_data['model']} does not exist on the Ollama server."
            )
        try:
            with httpx.stream(
                "POST",
                url=self.url + "api/chat",
                json=request_data,
                headers=headers,
                timeout=None,
            ) as response:
                response.encoding = "utf-8"
                if response.status_code != 200:
                    raise RuntimeError(f"Unexpected error: {response.status_code}")
                else:
                    if response.headers.get("Transfer-Encoding") == "chunked":
                        for chunk in response.iter_lines():
                            if chunk:
                                try:
                                    yield json.loads(chunk)["message"]["content"]
                                except json.JSONDecodeError:
                                    yield "Error: Failed to decode JSON response."
                    else:
                        # If the response is not chunked, read the entire conten
                        content = response.read().decode("utf-8")
                        try:
                            data = json.loads(content)
                            yield data["message"]["content"]
                        except (json.JSONDecodeError, KeyError):
                            yield f"Error: Invalid full JSON response\n{content}"

        except BaseException as e:
            yield f"Error occurred: {str(e)}\n\n"


if __name__ == "__main__":
    ollama_url = "http://127.0.0.1:6589/model_server/"
    gen_ai = OllamaHandler(url=ollama_url)

    model_name = "llama3.2:1b"
    prompt = """how r u?"""
    request_data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
    }

    start_time = time.time()
    gen_text = ""

    for res in gen_ai.chat(request_data=request_data):
        if isinstance(res, str):
            gen_text += res

    print(gen_text)

    print(f"\n time:{(time.time() - start_time)}")
