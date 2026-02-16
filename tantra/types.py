"""
Type definitions for LLM framework.
"""
from typing import TypedDict, Literal, Optional, Any, Callable, Awaitable
from enum import Enum


class ToolParameter(TypedDict, total=False):
    """OpenAI tool parameter definition."""
    type: str
    description: str
    enum: list[str]
    items: dict


class ToolFunction(TypedDict):
    """OpenAI tool function definition."""
    name: str
    description: str
    parameters: dict


class Tool(TypedDict):
    """OpenAI tool definition."""
    type: Literal["function"]
    function: ToolFunction


class Message(TypedDict, total=False):
    """Chat message."""
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str]
    tool_calls: Optional[list]
    tool_call_id: Optional[str]
    name: Optional[str]


class AgentConfig(TypedDict, total=False):
    """Agent configuration."""
    name: str
    model: str
    temperature: float
    max_tokens: Optional[int]
    max_iterations: int
    tool_choice: Literal["auto", "required", "none"]


class ToolExecutionResult(TypedDict):
    """Result of tool execution."""
    success: bool
    result: Any
    error: Optional[str]


class AgentResponse(TypedDict):
    """Agent execution response."""
    success: bool
    content: Optional[str]
    messages: list[Message]
    tool_calls: list[dict]
    iterations: int
    usage: dict[str, int]
    error: Optional[str]


# Type for async tool functions
AsyncToolFunction = Callable[..., Awaitable[Any]]
SyncToolFunction = Callable[..., Any]
ToolFunction = AsyncToolFunction | SyncToolFunction
