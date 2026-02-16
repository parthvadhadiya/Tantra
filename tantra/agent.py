"""
Base Agent class for LLM function calling.
"""
import copy
import json
import logging
from typing import Any, Callable, Optional

from .providers import LLMProvider, OpenAIProvider
from .types import (
    AgentConfig, AgentResponse, Message, Tool,
    AsyncToolFunction, SyncToolFunction
)
from .tools import generate_tool_schema, execute_tool, format_tool_result

logger = logging.getLogger(__name__)


class Agent:
    """
    Base agent class for LLM function calling with multi-agent support.

    Provides transparent, controlled execution of LLM with tools.
    No framework magic - full visibility into every request and response.

    Example:
        >>> agent = Agent(
        ...     name="CVE_Researcher",
        ...     system_message="You are a CVE research agent...",
        ...     tools=[fetch_news, fetch_cve_data],
        ...     model="gpt-4o"
        ... )
        >>>
        >>> response = await agent.run("Research CVE-2025-1234")
        >>> print(response['content'])
        
    Multi-Agent Example:
        >>> researcher = Agent(name="Researcher", ...)
        >>> writer = Agent(name="Writer", ...)
        >>> coordinator = Agent(
        ...     name="Coordinator",
        ...     tools=[researcher.as_tool(), writer.as_tool()]
        ... )
    """

    def __init__(
        self,
        name: str,
        system_message: str,
        tools: Optional[list[Callable]] = None,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        max_iterations: int = 20,
        tool_choice: str = "auto",
        truncate_tool_results: bool = True,
        provider: Optional[LLMProvider] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize agent.

        Args:
            name: Agent name (for logging/observability)
            system_message: System prompt defining agent behavior
            tools: List of tool functions (sync or async) or other agents
            model: LLM model to use (e.g., "gpt-4o", "gpt-4-turbo")
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Max tokens in response (None = no limit)
            max_iterations: Max tool-calling iterations to prevent loops
            tool_choice: "auto", "required", or "none"
            truncate_tool_results: Whether to truncate large tool results (default: True)
            provider: LLM provider instance (defaults to OpenAI)
            api_key: API key for default provider (optional, uses env var if not provided)
        """
        self.name = name
        self.system_message = system_message
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_iterations = max_iterations
        self.tool_choice = tool_choice
        self.truncate_tool_results = truncate_tool_results

        # Initialize provider
        self.provider = provider if provider is not None else OpenAIProvider(api_key=api_key)

        # Process tools
        self.tools = tools or []
        self.tool_map: dict[str, Callable] = {}  # Will be populated during schema generation
        self.tool_schemas = self._generate_tool_schemas()

        # Conversation history
        self.messages: list[Message] = []
        
        # Usage tracking
        self.total_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    def _generate_tool_schemas(self) -> list[Tool]:
        """Generate OpenAI tool schemas from tool functions."""
        schemas = []
        for tool in self.tools:
            try:
                # Generate schema from raw function
                schema = generate_tool_schema(tool)
                self.tool_map[tool.__name__] = tool

                schemas.append(schema)
                logger.debug(f"Generated schema for tool: {schema['function']['name']}")
            except Exception as e:
                tool_name = getattr(tool, '__name__', 'unknown')
                logger.error(f"Failed to generate schema for {tool_name}: {e}", exc_info=True)
        return schemas

    async def run(self, task: str, **kwargs) -> AgentResponse:
        """
        Run agent with given task.

        Handles full conversation loop with tool calling until
        agent returns final response or max iterations reached.

        Args:
            task: User task/prompt
            **kwargs: Additional parameters to override defaults

        Returns:
            Agent response with content, messages, and metadata
        """
        # Initialize conversation
        self.messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": task}
        ]

        iteration = 0
        tool_calls_made = []

        try:
            while iteration < self.max_iterations:
                iteration += 1
                logger.info(f"[{self.name}] Iteration {iteration}/{self.max_iterations}")

                # Call OpenAI API
                response = await self._call_openai()

                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                # Add assistant message to history
                message_dict = self._message_to_dict(message)
                self.messages.append(message_dict)

                logger.debug(f"[{self.name}] Finish reason: {finish_reason}")

                # If no tool calls, conversation is complete
                if finish_reason == "stop" or not message.tool_calls:
                    logger.info(f"[{self.name}] Completed in {iteration} iterations")
                    return {
                        "success": True,
                        "content": message.content,
                        "messages": self.messages,
                        "tool_calls": tool_calls_made,
                        "iterations": iteration,
                        "usage": self.total_usage.copy(),
                        "error": None
                    }

                # Execute tool calls
                if message.tool_calls:
                    await self._execute_tool_calls(message.tool_calls, tool_calls_made)

            # Max iterations reached
            logger.warning(f"[{self.name}] Max iterations ({self.max_iterations}) reached")
            return {
                "success": False,
                "content": None,
                "messages": self.messages,
                "tool_calls": tool_calls_made,
                "iterations": iteration,
                "usage": self.total_usage.copy(),
                "error": f"Max iterations ({self.max_iterations}) reached"
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error during execution: {e}", exc_info=True)
            return {
                "success": False,
                "content": None,
                "messages": self.messages,
                "tool_calls": tool_calls_made,
                "iterations": iteration,
                "usage": self.total_usage.copy(),
                "error": str(e)
            }

    async def _call_openai(self):
        """Make API call to LLM provider."""
        logger.debug(f"[{self.name}] Calling LLM: {self.model}")
        
        response = await self.provider.create_completion(
            messages=self.messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=self.tool_schemas if self.tool_schemas else None,
            tool_choice=self.tool_choice
        )
        
        # Track usage
        if "usage" in response:
            self.total_usage["prompt_tokens"] += response["usage"]["prompt_tokens"]
            self.total_usage["completion_tokens"] += response["usage"]["completion_tokens"]
            self.total_usage["total_tokens"] += response["usage"]["total_tokens"]
        
        # Convert standardized response back to OpenAI-like format for compatibility
        class MessageObj:
            def __init__(self, data):
                self.role = data["role"]
                self.content = data["content"]
                self.tool_calls = None
                if data.get("tool_calls"):
                    self.tool_calls = []
                    for tc in data["tool_calls"]:
                        class ToolCall:
                            def __init__(self, tc_data):
                                self.id = tc_data["id"]
                                self.type = tc_data["type"]
                                class Function:
                                    def __init__(self, func_data):
                                        self.name = func_data["name"]
                                        self.arguments = func_data["arguments"]
                                self.function = Function(tc_data["function"])
                        self.tool_calls.append(ToolCall(tc))
        
        class Choice:
            def __init__(self, message_data, finish_reason):
                self.message = MessageObj(message_data)
                self.finish_reason = finish_reason
        
        class Response:
            def __init__(self, data):
                self.choices = [Choice(data["message"], data["finish_reason"])]
        
        return Response(response)

    async def _execute_tool_calls(self, tool_calls, tool_calls_made: list):
        """Execute all tool calls from assistant message in parallel."""
        import asyncio

        # Log all tools being executed
        tool_names = [tc.function.name for tc in tool_calls]
        if len(tool_calls) > 1:
            logger.info(f"[{self.name}] Executing {len(tool_calls)} tools in parallel: {tool_names}")

        # Prepare all tool executions
        async def execute_single_tool(tool_call):
            tool_name = tool_call.function.name
            tool_args_str = tool_call.function.arguments

            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError as e:
                logger.error(f"[{self.name}] Invalid tool arguments JSON: {e}")
                tool_args = {}

            logger.info(f"[{self.name}] Executing tool: {tool_name}({list(tool_args.keys())})")

            # Execute tool
            result = await execute_tool(tool_name, tool_args, self.tool_map)

            logger.debug(f"[{self.name}] Tool {tool_name} completed: success={result['success']}")

            return (tool_call, tool_name, tool_args, result)

        # Execute all tool calls in parallel
        results = await asyncio.gather(*[execute_single_tool(tc) for tc in tool_calls])

        # Process results sequentially to maintain message order
        for tool_call, tool_name, tool_args, result in results:
            # Track tool call
            tool_calls_made.append({
                "tool": tool_name,
                "arguments": tool_args,
                "success": result["success"],
                "error": result["error"]
            })

            # Format result for chat
            if result["success"]:
                # Use truncation only if enabled (for agents that need to stay within context limits)
                # Impact/Enrich agents disable truncation so pipeline can access full tool responses
                if self.truncate_tool_results:
                    content = format_tool_result(result["result"], max_length=50000)
                else:
                    content = format_tool_result(result["result"], max_length=None)  # No truncation
            else:
                content = json.dumps({"error": result["error"]})

            # Add tool result to conversation
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": content
            })

    @staticmethod
    def _message_to_dict(message) -> Message:
        """Convert OpenAI message object to dictionary."""
        msg_dict: Message = {"role": message.role}

        if message.content:
            msg_dict["content"] = message.content

        if hasattr(message, 'tool_calls') and message.tool_calls:
            msg_dict["tool_calls"] = [
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

        return msg_dict

    def reset(self):
        """Reset conversation history."""
        self.messages = []
        logger.debug(f"[{self.name}] Conversation history reset")

    def get_messages(self) -> list[Message]:
        """Get current conversation history."""
        return self.messages.copy()

    def add_user_message(self, content: str):
        """Add a user message to conversation."""
        self.messages.append({"role": "user", "content": content})

    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response."""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant" and msg.get("content"):
                return msg["content"]
        return None
    
    def fork(self) -> "Agent":
        """
        Create a fork of this agent with copied conversation state.
        
        Useful for exploring multiple conversation paths in multi-agent systems.
        The forked agent has a deep copy of messages but shares tools and configuration.
        
        Returns:
            New Agent instance with copied state
            
        Example:
            >>> agent = Agent(name="Analyst", ...)
            >>> response1 = await agent.run("Analyze data")
            >>> 
            >>> # Fork to explore different paths
            >>> fork1 = agent.fork()
            >>> fork2 = agent.fork()
            >>> 
            >>> result1 = await fork1.run("Approach A")
            >>> result2 = await fork2.run("Approach B")
        """
        forked = Agent(
            name=f"{self.name}_fork",
            system_message=self.system_message,
            tools=self.tools.copy(),
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            max_iterations=self.max_iterations,
            tool_choice=self.tool_choice,
            truncate_tool_results=self.truncate_tool_results,
            provider=self.provider  # Share the same provider
        )
        
        # Deep copy messages and tool map
        forked.messages = copy.deepcopy(self.messages)
        forked.tool_map = self.tool_map.copy()
        forked.tool_schemas = self.tool_schemas.copy()
        
        logger.debug(f"[{self.name}] Created fork with {len(self.messages)} messages")
        
        return forked
    
    def as_tool(self, description: Optional[str] = None) -> Callable:
        """
        Convert this agent into a tool that can be used by other agents.
        
        Enables multi-agent coordination where one agent can delegate tasks
        to specialized sub-agents.
        
        Args:
            description: Optional custom description for the tool.
                        If not provided, uses the agent's system message.
        
        Returns:
            Async function that can be used as a tool by other agents
            
        Example:
            >>> researcher = Agent(
            ...     name="Researcher",
            ...     system_message="You research topics and provide detailed analysis."
            ... )
            >>> 
            >>> writer = Agent(
            ...     name="Writer",
            ...     system_message="You write engaging articles."
            ... )
            >>> 
            >>> coordinator = Agent(
            ...     name="Coordinator",
            ...     system_message="You coordinate research and writing tasks.",
            ...     tools=[researcher.as_tool(), writer.as_tool()]
            ... )
            >>> 
            >>> result = await coordinator.run("Write an article about AI")
        """
        agent = self
        tool_description = description or self.system_message.split('.')[0]
        
        async def agent_tool(task: str) -> dict:
            # Create a clean description from docstring
            nonlocal tool_description
            return tool_description
        
        # Set proper function metadata for schema generation
        agent_tool.__name__ = self.name.lower().replace(' ', '_')
        agent_tool.__doc__ = f"""
        Delegate task to {self.name} agent.
        
        {tool_description}
        
        Args:
            task: The task or question to delegate to the {self.name} agent
            
        Returns:
            Agent's response as a dictionary with the result
        """
        
        # Wrap the actual agent execution
        async def wrapped_agent_tool(task: str) -> dict:
            logger.info(f"[{agent.name}] Invoked as tool with task: {task[:100]}...")
            
            # Create a fork to avoid polluting the original agent's conversation
            forked_agent = agent.fork()
            response = await forked_agent.run(task)
            
            if response["success"]:
                return {
                    "status": "success",
                    "result": response["content"],
                    "agent": agent.name
                }
            else:
                return {
                    "status": "error",
                    "error": response["error"],
                    "agent": agent.name
                }
        
        # Copy metadata for schema generation
        wrapped_agent_tool.__name__ = agent_tool.__name__
        wrapped_agent_tool.__doc__ = agent_tool.__doc__
        
        return wrapped_agent_tool
