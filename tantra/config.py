from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .llm import LLMType

@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    instructions: str = ""
    llm_type: LLMType = LLMType.OPENAI
    llm_model: str = "gpt-4"
    llm_api_key: Optional[str] = None
    llm_options: Dict[str, Any] = field(default_factory=dict)
    memory_path: Optional[str] = None
    streaming: bool = True
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'AgentConfig':
        """Create config from dictionary"""
        if 'llm_type' in config:
            config['llm_type'] = LLMType(config['llm_type'])
        return cls(**config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'name': self.name,
            'instructions': self.instructions,
            'llm_type': self.llm_type.value,
            'llm_model': self.llm_model,
            'llm_api_key': self.llm_api_key,
            'llm_options': self.llm_options,
            'memory_path': self.memory_path,
            'streaming': self.streaming
        }
