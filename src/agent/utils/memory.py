"""
Memory module for the simple agent.
Provides persistent storage and retrieval of conversation history and agent state.
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class Memory:
    """
    Simple JSON-based memory system for storing conversation history and agent state.
    """
    
    def __init__(self, memory_file: str = "memory.json"):
        """
        Initialize the memory system.
        
        Args:
            memory_file (str): Path to the JSON file for storing memory data
        """
        self.memory_file = memory_file
        self.data = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """
        Load memory data from the JSON file.
        
        Returns:
            Dict[str, Any]: The loaded memory data or empty structure if file doesn't exist
        """
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure required structure exists
                    if 'conversations' not in data:
                        data['conversations'] = []
                    if 'agent_state' not in data:
                        data['agent_state'] = {}
                    if 'metadata' not in data:
                        data['metadata'] = {
                            'created_at': datetime.now().isoformat(),
                            'last_updated': datetime.now().isoformat()
                        }
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load memory file {self.memory_file}: {e}")
                return self._create_empty_memory()
        else:
            return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict[str, Any]:
        """
        Create an empty memory structure.
        
        Returns:
            Dict[str, Any]: Empty memory structure
        """
        return {
            'conversations': [],
            'agent_state': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _save_memory(self) -> bool:
        """
        Save memory data to the JSON file.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Update last_updated timestamp
            self.data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error: Could not save memory file {self.memory_file}: {e}")
            return False
    
    def add_conversation_turn(self, user_input: str, agent_response: str, 
                            tools_used: Optional[List[str]] = None) -> bool:
        """
        Add a conversation turn to memory.
        
        Args:
            user_input (str): The user's input
            agent_response (str): The agent's response
            tools_used (Optional[List[str]]): List of tools used in this turn
            
        Returns:
            bool: True if successfully added and saved
        """
        conversation_turn = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'tools_used': tools_used or []
        }
        
        self.data['conversations'].append(conversation_turn)
        return self._save_memory()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation turns.
        
        Args:
            limit (int): Maximum number of conversation turns to return
            
        Returns:
            List[Dict[str, Any]]: Recent conversation turns
        """
        return self.data['conversations'][-limit:] if self.data['conversations'] else []
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get all conversation turns.
        
        Returns:
            List[Dict[str, Any]]: All conversation turns
        """
        return self.data['conversations']
    
    def update_agent_state(self, key: str, value: Any) -> bool:
        """
        Update agent state information.
        
        Args:
            key (str): The state key
            value (Any): The state value
            
        Returns:
            bool: True if successfully updated and saved
        """
        self.data['agent_state'][key] = value
        return self._save_memory()
    
    def get_agent_state(self, key: str, default: Any = None) -> Any:
        """
        Get agent state information.
        
        Args:
            key (str): The state key
            default (Any): Default value if key doesn't exist
            
        Returns:
            Any: The state value or default
        """
        return self.data['agent_state'].get(key, default)
    
    def clear_conversations(self) -> bool:
        """
        Clear all conversation history.
        
        Returns:
            bool: True if successfully cleared and saved
        """
        self.data['conversations'] = []
        return self._save_memory()
    
    def clear_agent_state(self) -> bool:
        """
        Clear all agent state.
        
        Returns:
            bool: True if successfully cleared and saved
        """
        self.data['agent_state'] = {}
        return self._save_memory()
    
    def clear_all(self) -> bool:
        """
        Clear all memory data.
        
        Returns:
            bool: True if successfully cleared and saved
        """
        self.data = self._create_empty_memory()
        return self._save_memory()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dict[str, Any]: Memory statistics including conversation count, file size, etc.
        """
        stats = {
            'conversation_count': len(self.data['conversations']),
            'agent_state_keys': len(self.data['agent_state']),
            'memory_file': self.memory_file,
            'file_exists': os.path.exists(self.memory_file),
            'metadata': self.data['metadata']
        }
        
        if os.path.exists(self.memory_file):
            stats['file_size_bytes'] = os.path.getsize(self.memory_file)
        
        return stats