"""
Core agent module for the simple agent system.
Handles user input processing, tool usage, and response generation.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

from jinja2 import DictLoader, Environment

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agent.utils.memory import Memory
from GenAIServices.ollama import OllamaHandler
from tools.register import ToolManager


class SimpleAgent:
    """
    Main agent class that processes user input and generates responses using LLM and tools.
    """

    def __init__(
        self,
        ollama_url: str = "http://127.0.0.1:6589/model_server/",
        model_name: str = "llama3.2:1b",
        memory_file: str = "memory.json",
    ):
        """
        Initialize the Simple Agent.

        Args:
            ollama_url (str): URL for the Ollama service
            model_name (str): Name of the model to use
            memory_file (str): Path to the memory file
        """
        self.ollama_handler = OllamaHandler(url=ollama_url)
        self.model_name = model_name
        self.tool_manager = ToolManager()
        self.memory = Memory(memory_file=memory_file)
        self.prompts = self._load_prompts()
        self.jinja_env = Environment(loader=DictLoader(self.prompts))

    def _load_prompts(self) -> Dict[str, Any]:
        """
        Load prompts from the prompt.json file.

        Returns:
            Dict[str, Any]: Loaded prompts
        """
        prompt_file = os.path.join(os.path.dirname(__file__), "utils", "prompt.json")
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load prompts from {prompt_file}: {e}")
            return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, Any]:
        """
        Get default prompts if prompt file cannot be loaded.

        Returns:
            Dict[str, Any]: Default prompts
        """
        return {
            "system_prompt": "You are a helpful AI assistant.",
            "tool_selection_prompt": "Analyze if tools are needed for: {{ user_input }}. Available tools: {{ available_tools }}",
            "response_generation_prompt": "Respond to: {{ user_input }}",
            "summary_prompt": "Summarize this interaction.",
            "error_handling_prompt": "Handle this error: {{ error_message }}",
        }

    def _render_template(self, template_name: str, **kwargs) -> str:
        """
        Render a Jinja2 template with the given variables.

        Args:
            template_name (str): Name of the template to render
            **kwargs: Variables to pass to the template

        Returns:
            str: Rendered template
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            print(f"Warning: Could not render template {template_name}: {e}")
            # Fallback to simple string formatting if Jinja2 fails
            if template_name in self.prompts:
                return self.prompts[template_name].format(**kwargs)
            return str(kwargs)

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the LLM with a given prompt.

        Args:
            prompt (str): The user prompt
            system_prompt (Optional[str]): Optional system prompt

        Returns:
            str: Generated response from LLM
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        request_data = {"model": self.model_name, "messages": messages}

        try:
            response_text = ""
            for chunk in self.ollama_handler.chat(request_data=request_data):
                if isinstance(chunk, str):
                    response_text += chunk
            return response_text.strip()
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def _analyze_tool_needs(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze if the user input requires any tools.

        Args:
            user_input (str): The user's input

        Returns:
            Dict[str, Any]: Analysis result including tools to use
        """
        available_tools = self.tool_manager.get_available_tools()
        tools_info = json.dumps(available_tools, indent=2)

        prompt = self._render_template(
            "tool_selection_prompt", user_input=user_input, available_tools=tools_info
        )

        response = self._call_llm(prompt)

        # Clean the response - remove any extra text before/after JSON
        response = response.strip()

        # Try to find JSON object in the response
        start_idx = response.find("{")
        end_idx = response.rfind("}")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx : end_idx + 1]
            analysis = json.loads(json_str)

            if not isinstance(analysis, dict):
                raise ValueError("Response is not a valid JSON object")

            # Ensure required keys exist
            if "needs_tools" not in analysis:
                analysis["needs_tools"] = False
            if "tools_to_use" not in analysis:
                analysis["tools_to_use"] = []
            if "reasoning" not in analysis:
                analysis["reasoning"] = "No reasoning provided"

            return analysis
        else:
            raise ValueError("No valid JSON found in response")

    def _execute_tools(self, tools_to_use: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Execute the specified tools.

        Args:
            tools_to_use (List[Dict[str, Any]]): List of tools and their parameters

        Returns:
            Dict[str, str]: Results from tool execution
        """
        tool_results = {}

        for tool_spec in tools_to_use:
            tool_name = tool_spec.get("tool_name", "")
            parameters = tool_spec.get("parameters", {})

            if tool_name:
                result = self.tool_manager.execute_tool(tool_name, parameters)
                tool_results[tool_name] = result

        return tool_results

    def _generate_response(
        self, user_input: str, tool_results: Dict[str, str] = None
    ) -> str:
        """
        Generate a response to the user input, incorporating tool results if available.

        Args:
            user_input (str): The user's input
            tool_results (Dict[str, str]): Results from tool execution

        Returns:
            str: Generated response
        """
        # Get recent conversation history for context
        recent_conversations = self.memory.get_recent_conversations(limit=3)
        conversation_context = ""

        for conv in recent_conversations:
            conversation_context += f"User: {conv['user_input']}\n"
            conversation_context += f"Assistant: {conv['agent_response']}\n\n"

        # Format tool results
        tool_results_text = ""
        if tool_results:
            tool_results_text = json.dumps(tool_results, indent=2)

        prompt = self._render_template(
            "response_generation_prompt",
            user_input=user_input,
            tool_results=tool_results_text,
            conversation_history=conversation_context,
        )

        return self._call_llm(prompt, self.prompts["system_prompt"])

    def _generate_summary(
        self, user_input: str, agent_response: str, tools_used: List[str]
    ) -> str:
        """
        Generate a summary of the conversation turn.

        Args:
            user_input (str): The user's input
            agent_response (str): The agent's response
            tools_used (List[str]): List of tools used

        Returns:
            str: Generated summary
        """
        prompt = self._render_template(
            "summary_prompt",
            user_input=user_input,
            agent_response=agent_response,
            tools_used=tools_used,
        )

        return self._call_llm(prompt)

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Main function to process user input and generate a response.

        Args:
            user_input (str): The user's input

        Returns:
            Dict[str, Any]: Processing result including response, tools used, and summary
        """
        try:
            # Step 1: Analyze if tools are needed
            tool_analysis = self._analyze_tool_needs(user_input)

            # Step 2: Execute tools if needed
            tool_results = {}
            tools_used = []

            if tool_analysis.get("needs_tools", False):
                tools_to_use = tool_analysis.get("tools_to_use", [])
                tool_results = self._execute_tools(tools_to_use)
                tools_used = list(tool_results.keys())

            # Step 3: Generate response
            agent_response = self._generate_response(user_input, tool_results)

            # Step 4: Generate summary
            summary = self._generate_summary(user_input, agent_response, tools_used)

            # Step 5: Save to memory
            self.memory.add_conversation_turn(user_input, agent_response, tools_used)

            return {
                "response": agent_response,
                "tools_used": tools_used,
                "tool_results": tool_results,
                "summary": summary,
                "tool_analysis": tool_analysis,
            }

        except Exception as e:
            error_message = str(e)
            error_prompt = self._render_template(
                "error_handling_prompt",
                error_message=error_message,
                user_input=user_input,
            )
            error_response = self._call_llm(error_prompt)

            return {
                "response": error_response,
                "tools_used": [],
                "tool_results": {},
                "summary": f"Error occurred: {error_message}",
                "error": error_message,
            }

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dict[str, Any]: Memory statistics
        """
        return self.memory.get_memory_stats()

    def clear_memory(self) -> bool:
        """
        Clear all memory.

        Returns:
            bool: True if successfully cleared
        """
        return self.memory.clear_all()

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.

        Returns:
            List[str]: Available tool names
        """
        return self.tool_manager.get_tool_names()
