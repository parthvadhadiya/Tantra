from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

class LLMType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    # Add more providers as needed

class LLMConfig:
    def __init__(self, 
                 provider: LLMType,
                 model: str,
                 api_key: Optional[str] = None,
                 **kwargs):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.extra_config = kwargs

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def stream_chat(self, prompt: str, **kwargs) -> str:
        pass

class LLMFactory:
    @staticmethod
    def create(config: LLMConfig) -> BaseLLM:
        if config.provider == LLMType.OPENAI:
            from .providers.openai import OpenAILLM
            return OpenAILLM(config)
        elif config.provider == LLMType.ANTHROPIC:
            from .providers.anthropic import AnthropicLLM
            return AnthropicLLM(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")
