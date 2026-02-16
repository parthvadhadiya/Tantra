"""
Tantra - A clean, transparent LLM framework for OpenAI function calling.

Tantra provides straightforward agent orchestration without framework magic.
Full visibility into every API call and tool execution.

Example:
    >>> from tantra import Agent
    >>>
    >>> agent = Agent(
    ...     name="Researcher",
    ...     system_message="You are a helpful research assistant.",
    ...     tools=[search_web, fetch_data],
    ...     model="gpt-4o"
    ... )
    >>>
    >>> response = await agent.run("Research recent AI developments")
    >>> print(response['content'])
"""

from .agent import Agent
from .providers import LLMProvider, OpenAIProvider
from .types import (
    AgentConfig,
    AgentResponse,
    Tool,
    ToolExecutionResult,
    Message,
)
from .tools import (
    generate_tool_schema,
    execute_tool,
    format_tool_result,
)
from .utils import (
    extract_json_from_response,
    extract_html_from_response,
    truncate_for_logging,
    count_tokens_estimate,
    format_error_for_display,
    merge_tool_responses,
)

__all__ = [
    # Main classes
    "Agent",
    
    # Providers
    "LLMProvider",
    "OpenAIProvider",

    # Types
    "AgentConfig",
    "AgentResponse",
    "Tool",
    "ToolExecutionResult",
    "Message",

    # Tool utilities
    "generate_tool_schema",
    "execute_tool",
    "format_tool_result",

    # General utilities
    "extract_json_from_response",
    "extract_html_from_response",
    "truncate_for_logging",
    "count_tokens_estimate",
    "format_error_for_display",
    "merge_tool_responses",
]

__version__ = "0.1.0"
