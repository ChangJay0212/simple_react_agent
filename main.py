#!/usr/bin/env python3
"""
Main entry point for the Simple Agent application.
This script provides a command-line interface for interacting with the agent.
"""

import argparse
import os
import sys

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from agent.core import SimpleAgent


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("Simple Agent - AI Assistant with Tool Support")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'bye' to exit")
    print("Type 'help' for available commands")
    print("Type 'stats' to see memory statistics")
    print("Type 'clear' to clear memory")
    print("Type 'tools' to see available tools")
    print("-" * 60)


def print_help():
    """Print help information."""
    print("\nAvailable Commands:")
    print("  help    - Show this help message")
    print("  stats   - Show memory and agent statistics")
    print("  clear   - Clear all conversation memory")
    print("  tools   - Show available tools")
    print("  quit    - Exit the application")
    print("  exit    - Exit the application")
    print("  bye     - Exit the application")
    print("\nTips:")
    print("  - Ask about current time to test the time tool")
    print("  - The agent remembers your conversation history")
    print("  - Try asking questions that might need tool assistance")
    print()


def handle_special_commands(user_input: str, agent: SimpleAgent) -> bool:
    """
    Handle special commands like help, stats, etc.

    Args:
        user_input (str): The user's input
        agent (SimpleAgent): The agent instance

    Returns:
        bool: True if command was handled, False otherwise
    """
    command = user_input.lower().strip()

    if command == "help":
        print_help()
        return True

    elif command == "stats":
        stats = agent.get_memory_stats()
        print("\nAgent Statistics:")
        print(f"  Conversations: {stats['conversation_count']}")
        print(f"  Agent state keys: {stats['agent_state_keys']}")
        print(f"  Memory file: {stats['memory_file']}")
        print(f"  File exists: {stats['file_exists']}")
        if "file_size_bytes" in stats:
            print(f"  File size: {stats['file_size_bytes']} bytes")
        print(f"  Created: {stats['metadata']['created_at']}")
        print(f"  Last updated: {stats['metadata']['last_updated']}")
        print()
        return True

    elif command == "clear":
        if agent.clear_memory():
            print("Memory cleared successfully!")
        else:
            print("Failed to clear memory.")
        print()
        return True

    elif command == "tools":
        tools = agent.get_available_tools()
        print(f"\nAvailable Tools ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool}")
        print()
        return True

    elif command in ["quit", "exit", "bye"]:
        print("\nGoodbye! Thanks for using Simple Agent!")
        return True

    return False


def interactive_mode(agent: SimpleAgent):
    """
    Run the agent in interactive mode.

    Args:
        agent (SimpleAgent): The agent instance
    """
    print_banner()

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if handle_special_commands(user_input, agent):
                if user_input.lower().strip() in ["quit", "exit", "bye"]:
                    break
                continue

            # Process user input with the agent
            print("\nThinking...")
            result = agent.process_user_input(user_input)

            # Display the response
            print(f"\nAgent: {result['response']}")

            # Show tools used if any
            if result["tools_used"]:
                print(f"\nTools used: {', '.join(result['tools_used'])}")

            # Show summary if available
            if result.get("summary"):
                print(f"\nSummary: {result['summary']}")

            # Show error if any
            if "error" in result:
                print(f"\nError: {result['error']}")

        except KeyboardInterrupt:
            print("\n\nGoodbye! Thanks for using Simple Agent!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            print("Please try again or type 'quit' to exit.")


def single_query_mode(agent: SimpleAgent, query: str):
    """
    Process a single query and exit.

    Args:
        agent (SimpleAgent): The agent instance
        query (str): The query to process
    """
    print(f"Query: {query}")
    print("Processing...")

    result = agent.process_user_input(query)

    print(f"Response: {result['response']}")

    if result["tools_used"]:
        print(f"Tools used: {', '.join(result['tools_used'])}")

    if "error" in result:
        print(f"Error: {result['error']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Simple Agent - AI Assistant with Tool Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Start interactive mode
  python main.py -q "What time is it?"     # Single query mode
  python main.py --ollama-url http://localhost:11434/  # Custom Ollama URL
  python main.py --model llama2            # Use different model
        """,
    )

    parser.add_argument(
        "-q", "--query", type=str, help="Process a single query and exit"
    )

    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://10.204.16.64:6589/model_server/",
        help="Ollama service URL (default: http://10.204.16.64:6589/model_server/)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-oss:20b",
        help="Model name to use (default: gpt-oss:20b)",
    )

    parser.add_argument(
        "--memory-file",
        type=str,
        default="memory.json",
        help="Memory file path (default: memory.json)",
    )

    args = parser.parse_args()

    # Initialize the agent
    print("Initializing Simple Agent...")
    agent = SimpleAgent(
        ollama_url=args.ollama_url,
        model_name=args.model,
        memory_file=args.memory_file,
    )
    print("Agent initialized successfully!")

    # Run in appropriate mode
    if args.query:
        single_query_mode(agent, args.query)
    else:
        interactive_mode(agent)


if __name__ == "__main__":
    main()
