from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from .utils.logger import logger
from .models.parameter_store import ToolParameterStore

class Memory:
    """Memory class for storing conversation history, facts, and tool parameters"""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.facts: Dict[str, str] = {}
        self.parameter_store: Optional[ToolParameterStore] = None
        self.last_accessed: Dict[str, datetime] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        logger.debug(f"Adding message: {json.dumps(message, indent=2)}")
        self.messages.append(message)
        self.last_accessed["messages"] = datetime.now()
    
    def add_fact(self, key: str, value: str):
        """Store a fact about the conversation or user"""
        logger.debug(f"Adding fact: {key} = {value}")
        self.facts[key] = value
        self.last_accessed[key] = datetime.now()
    
    def get_fact(self, key: str) -> Optional[str]:
        """Retrieve a stored fact"""
        logger.debug(f"Getting fact: {key}")
        if key in self.facts:
            self.last_accessed[key] = datetime.now()
            return self.facts[key]
        return None
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversations[-limit:]
    
    def start_collecting_params(self, tool_name: str) -> None:
        """Start collecting parameters for a tool"""
        logger.debug(f"Starting parameter collection for {tool_name}")
        self.parameter_store = ToolParameterStore(tool_name=tool_name)
        # Add fact to track current tool
        self.add_fact("current_tool", tool_name)
    
    def add_param(self, tool_name: str, param_name: str, value: Any) -> None:
        """Add a collected parameter value"""
        if not self.parameter_store or self.parameter_store.tool_name != tool_name:
            self.start_collecting_params(tool_name)
        
        logger.debug(f"Adding parameter for {tool_name}: {param_name}={value}")
        self.parameter_store.add_parameter(param_name, value)
        # Store param in facts for context
        self.add_fact(f"{tool_name}_{param_name}", str(value))
    
    def get_collected_params(self, tool_name: str) -> Dict[str, Any]:
        """Get collected parameters for a tool"""
        if not self.parameter_store or self.parameter_store.tool_name != tool_name:
            logger.debug(f"No parameters found for {tool_name}")
            return {}
            
        params = self.parameter_store.get_all_parameters()
        logger.debug(f"Retrieved parameters for {tool_name}: {params}")
        return params
    
    def clear_collected_params(self, tool_name: str) -> None:
        """Clear collected parameters for a tool"""
        if self.parameter_store and self.parameter_store.tool_name == tool_name:
            logger.debug(f"Clearing parameters for {tool_name}")
            self.parameter_store = None
            # Clear facts related to this tool
            current_tool = self.get_fact("current_tool")
            if current_tool == tool_name:
                self.facts = {k: v for k, v in self.facts.items() 
                            if not k.startswith(tool_name)}
                self.facts.pop("current_tool", None)
    
    def get_context(self) -> str:
        """Get formatted context for LLM"""
        # Format facts
        facts = [f"- {k}: {v}" for k, v in self.facts.items()]
        facts_str = "Known facts:\n" + "\n".join(facts) if facts else ""
        
        # Format conversation history
        history = []
        for msg in self.messages[-5:]:  # Last 5 messages
            role = msg["role"]
            content = msg["content"]
            history.append(f"{role}: {content}")
        history_str = "Recent conversation:\n" + "\n".join(history) if history else ""
        
        # Combine all context
        context_parts = [p for p in [facts_str, history_str] if p]
        return "\n\n".join(context_parts)
    
    def save(self, path: str):
        """Save memory to file"""
        with open(path, 'w') as f:
            json.dump({
                "conversations": self.conversations,
                "facts": self.facts,
                "last_accessed": {k: v.isoformat() for k, v in self.last_accessed.items()}
            }, f)
    
    @classmethod
    def load(cls, path: str) -> 'Memory':
        """Load memory from file"""
        memory = cls()
        with open(path, 'r') as f:
            data = json.load(f)
            memory.conversations = data["conversations"]
            memory.facts = data["facts"]
            memory.last_accessed = {
                k: datetime.fromisoformat(v) 
                for k, v in data["last_accessed"].items()
            }
        return memory
