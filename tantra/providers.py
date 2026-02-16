"""
LLM Provider abstraction for different AI backends.

This module provides a lightweight abstraction layer for different LLM providers.
Currently supports OpenAI, with extensibility for community contributions.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Base class for LLM providers.
    
    Implement this interface to add support for new LLM providers
    (e.g., Anthropic, Gemini, Ollama, etc.)
    """
    
    @abstractmethod
    async def create_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        tools: Optional[list[dict]] = None,
        tool_choice: str = "auto"
    ) -> dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            messages: List of conversation messages
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: List of tool definitions (OpenAI format)
            tool_choice: Tool choice strategy ("auto", "required", "none")
            
        Returns:
            Dictionary with standardized response format:
            {
                "message": {
                    "role": "assistant",
                    "content": str | None,
                    "tool_calls": list | None
                },
                "finish_reason": str,
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                }
            }
        """
        pass


class OpenAIProvider(LLMProvider):
    """
    OpenAI provider implementation.
    
    Supports GPT-4, GPT-3.5, and other OpenAI models with function calling.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (uses env var OPENAI_API_KEY if not provided)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        logger.debug("Initialized OpenAI provider")
    
    async def create_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        tools: Optional[list[dict]] = None,
        tool_choice: str = "auto"
    ) -> dict[str, Any]:
        """
        Create completion using OpenAI API.
        
        Args:
            messages: Conversation messages
            model: OpenAI model name (e.g., "gpt-4o", "gpt-4-turbo")
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            tools: Tool definitions in OpenAI format
            tool_choice: Tool choice strategy
            
        Returns:
            Standardized response dictionary
        """
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        
        logger.debug(f"OpenAI API call: model={model}, messages={len(messages)}")
        
        response = await self.client.chat.completions.create(**params)
        
        # Convert to standardized format
        choice = response.choices[0]
        message = choice.message
        
        result = {
            "message": {
                "role": message.role,
                "content": message.content,
                "tool_calls": None
            },
            "finish_reason": choice.finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        # Add tool calls if present
        if hasattr(message, 'tool_calls') and message.tool_calls:
            result["message"]["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        
        return result
