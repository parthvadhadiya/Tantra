# Tantra

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vendorable](https://img.shields.io/badge/vendorable-copy%20%26%20customize-green.svg)](VENDORING.md)
[![Code Size](https://img.shields.io/badge/core_size-~1200_lines-brightgreen.svg)](tantra/)

**Transparent LLM agent patterns you can understand, copy, and make your own.**

Not another AI framework with hidden magic. Tantra is a **reference implementation** you can use as-is or vendor into your project for full control.

## Two Ways to Use Tantra

### Option 1: Install as Library (Quick Start)

```bash
pip install tantra
```

Perfect for prototyping and projects that don't need customization.

### Option 2: Vendor into Your Project (Full Control)

```bash
# Easy way: Download and use the vendor script
curl -O https://raw.githubusercontent.com/axlnet/tantra/main/vendor.py
python vendor.py myproject/agents/

# Or manually copy the tantra/ folder
cp -r path/to/tantra/tantra/ myproject/agents/

# Only dependency needed
pip install openai
```

**No framework magic. Just ~1200 lines of transparent, readable code you own and can modify.**

👉 **See [VENDORING.md](VENDORING.md) for the complete guide**

## Why Tantra?

- **No Magic**: Explicit conversation state, tool schemas auto-generated from code
- **Full Transparency**: See every API call and tool execution
- **Vendorable**: Copy the code, make it yours, modify anything
- **Multi-Agent Ready**: Agent-as-tool pattern and conversation forking
- **Provider Agnostic**: Lightweight abstraction (OpenAI supported, community can add others)
- **Async-First**: All operations use async/await for performance
- **Truly Lightweight**: Core is ~1200 lines you can read in 30 minutes

## Philosophy: Not Another Framework

**The Problem**: AI frameworks are either too heavy with abstraction layers, or "lightweight" but still hide behavior you can't easily modify.

**Tantra's Solution**: Readable reference implementation you can use directly OR copy into your project.

### When to Vendor (Copy the Code)

Choose vendoring if you:
- 🎯 Need to modify agent behavior for your use case
- 🔍 Want to understand exactly how your agents work
- 🚫 Dislike "framework magic" or hidden abstractions
- 🛠️ Need custom logging, metrics, or integrations
- ⚡ Want to optimize for your specific performance needs

### When to Install (pip install)

Choose traditional install if you:
- 🚀 Want quick prototyping
- 📦 Don't need customization
- 🔄 Want automatic updates
- 👥 Prefer standard dependency management

**Both are first-class approaches.** The choice is yours.

## Quick Start

### Basic Agent (No Tools)

```python
import asyncio
from tantra import Agent

async def main():
    agent = Agent(
        name="Summarizer",
        system_message="You are a concise summarizer.",
        model="gpt-4o"
    )

    response = await agent.run("Explain quantum computing in 2 sentences.")
    print(response['content'])

asyncio.run(main())
```

### Agent with Tools

```python
import asyncio
from tantra import Agent

async def fetch_weather(city: str) -> dict:
    """
    Fetch weather data for a city.

    Args:
        city: City name

    Returns:
        Weather data dictionary
    """
    # Your weather API logic here
    return {"city": city, "temperature": 72, "condition": "Sunny"}

async def main():
    agent = Agent(
        name="WeatherBot",
        system_message="You are a weather assistant. Use fetch_weather to get data.",
        tools=[fetch_weather],
        model="gpt-4o"
    )

    response = await agent.run("What's the weather in Tokyo?")

    print(f"Success: {response['success']}")
    print(f"Response: {response['content']}")
    print(f"Tools called: {len(response['tool_calls'])}")

asyncio.run(main())
```

## Multi-Agent Features

Tantra supports advanced multi-agent patterns for building complex, coordinated agent systems.

### Agent-as-Tool Pattern

Use one agent as a tool for another, enabling specialized agent coordination:

```python
# Create specialized agents
researcher = Agent(
    name="Researcher",
    system_message="You research topics and provide detailed analysis.",
    model="gpt-4o"
)

writer = Agent(
    name="Writer",
    system_message="You write engaging articles.",
    model="gpt-4o"
)

# Coordinator uses other agents as tools
coordinator = Agent(
    name="Coordinator",
    system_message="You coordinate research and writing tasks.",
    tools=[
        researcher.as_tool(),  # Agent as a tool!
        writer.as_tool()
    ],
    model="gpt-4o"
)

# Coordinator automatically delegates to specialized agents
response = await coordinator.run("Create an article about quantum computing")
```

### Conversation Forking

Fork agent conversations to explore multiple paths:

```python
agent = Agent(name="Analyst", ...)

# Initial conversation
await agent.run("Analyze sales data")

# Fork to explore different approaches
fork1 = agent.fork()
fork2 = agent.fork()

# Explore paths in parallel
results = await asyncio.gather(
    fork1.run("Focus on seasonal patterns"),
    fork2.run("Focus on market trends")
)
```

### Usage Tracking

Every response includes token usage information:

```python
response = await agent.run("Task")

# Access usage data
print(response['usage'])
# {
#     "prompt_tokens": 150,
#     "completion_tokens": 75,
#     "total_tokens": 225
# }
```

## Core Concepts

### Agent

The `Agent` class is the heart of Tantra. It manages conversation state, tool execution, and OpenAI API calls.

```python
agent = Agent(
    name="MyAgent",                    # Agent name (for logging)
    system_message="Your behavior",    # System prompt
    tools=[func1, func2],              # List of tool functions
    model="gpt-4o",                    # OpenAI model
    temperature=0.0,                   # Sampling temperature
    max_tokens=None,                   # Max response tokens
    max_iterations=20,                 # Max tool-calling loops
    tool_choice="auto",                # "auto", "required", "none"
    truncate_tool_results=True,        # Truncate large tool outputs
    api_key=None                       # OpenAI API key (optional)
)
```

### Tool Functions

Tools are just regular Python functions (sync or async) with type hints and docstrings:

```python
async def search_database(query: str, limit: int = 10) -> dict:
    """
    Search the database for records.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        Search results dictionary
    """
    # Your logic here
    return {"results": [...]}
```

Tantra automatically generates OpenAI tool schemas from:
- Function signature and type hints
- Docstring (Google-style format)
- Required vs optional parameters

### Running an Agent

```python
response = await agent.run("Your task here")

# Response structure:
{
    "success": True,              # Whether execution completed successfully
    "content": "...",             # Final agent response
    "messages": [...],            # Full conversation history
    "tool_calls": [...],          # List of all tool calls made
    "iterations": 3,              # Number of iterations
    "error": None                 # Error message if failed
}
```

### Accessing Conversation History

```python
# Get all messages
messages = agent.get_messages()

# Get last assistant response
last_response = agent.get_last_response()

# Reset conversation
agent.reset()

# Add a user message manually
agent.add_user_message("Additional context")
```

## Advanced Features

### LLM Provider Abstraction

Tantra uses a provider abstraction layer for LLM backends. Currently supports OpenAI, with extensibility for community contributions.

```python
from tantra import Agent, OpenAIProvider

# Default: Uses OpenAI
agent = Agent(name="Agent", system_message="...", model="gpt-4o")

# Explicit provider
provider = OpenAIProvider(api_key="your-key")
agent = Agent(
    name="Agent",
    system_message="...",
    provider=provider,
    model="gpt-4o"
)
```

**Contributing a Provider**: Implement the `LLMProvider` interface to add support for other LLMs (Anthropic, Gemini, Ollama, etc.):

```python
from tantra import LLMProvider

class CustomProvider(LLMProvider):
    async def create_completion(self, messages, model, **kwargs):
        # Your implementation
        return {
            "message": {...},
            "finish_reason": "stop",
            "usage": {...}
        }
```

### JSON Response Extraction

```python
from tantra import extract_json_from_response

agent = Agent(
    name="DataExtractor",
    system_message="Return results as JSON: {\"key\": \"value\"}",
    model="gpt-4o"
)

response = await agent.run("Extract data")
json_data = extract_json_from_response(response['content'])
```

### HTML Response Extraction

```python
from tantra import extract_html_from_response

agent = Agent(
    name="ReportGenerator",
    system_message="Generate HTML reports",
    model="gpt-4o"
)

response = await agent.run("Create a report")
html = extract_html_from_response(response['content'])
```

### Error Handling

```python
response = await agent.run("Task")

if not response['success']:
    print(f"Error: {response['error']}")

    # Check which tools failed
    for tool_call in response['tool_calls']:
        if not tool_call['success']:
            print(f"Tool {tool_call['tool']} failed: {tool_call['error']}")
```

### Custom Tool Result Truncation

```python
# Disable truncation for agents that need full tool outputs
agent = Agent(
    name="DataProcessor",
    system_message="Process all data",
    tools=[large_data_fetcher],
    truncate_tool_results=False  # Get full tool outputs
)
```

## Design Philosophy

### Transparency Over Magic

Unlike heavy frameworks, Tantra doesn't hide what's happening:

```python
# After running an agent, you can see everything:
response = await agent.run("Research CVE-2025-1234")

# Full conversation including tool calls
for msg in response['messages']:
    print(f"{msg['role']}: {msg.get('content', 'tool call')[:50]}...")

# Exactly which tools were called and what they returned
for tc in response['tool_calls']:
    print(f"Tool: {tc['tool']}, Args: {tc['arguments']}, Success: {tc['success']}")
```

### No Hidden State

```python
# Conversation state is explicit and accessible
agent.messages  # Direct access to message list
agent.get_messages()  # Get a copy
agent.reset()  # Clear state explicitly
```

### Direct OpenAI API

Tantra doesn't wrap the OpenAI API - it uses it directly:

```python
# You can inspect the exact parameters sent to OpenAI
# by checking the agent's _call_openai() method source code
# No hidden transformations or middleware
```

## API Reference

### Agent

#### Constructor

```python
Agent(
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
)
```

#### Methods

- `async run(task: str, **kwargs) -> AgentResponse`: Run agent with task
- `reset()`: Clear conversation history
- `get_messages() -> list[Message]`: Get conversation history
- `add_user_message(content: str)`: Add user message
- `get_last_response() -> Optional[str]`: Get last assistant response
- `fork() -> Agent`: Create a fork with copied conversation state
- `as_tool(description: Optional[str] = None) -> Callable`: Convert agent to a tool for multi-agent use

### LLMProvider

Base class for LLM providers. Implement to add support for new providers.

#### Methods

- `async create_completion(...) -> dict`: Create a chat completion (abstract)

### Utilities

#### Response Parsing

- `extract_json_from_response(text: str) -> Optional[dict]`: Extract JSON from response
- `extract_html_from_response(text: str) -> Optional[str]`: Extract HTML from response

#### Tool Management

- `generate_tool_schema(func: Callable) -> Tool`: Generate OpenAI tool schema
- `format_tool_result(result: Any, max_length: int) -> str`: Format tool output

#### General Utilities

- `truncate_for_logging(text: str, max_length: int) -> str`: Truncate text
- `count_tokens_estimate(text: str) -> int`: Estimate token count
- `format_error_for_display(error: Exception) -> str`: Format exception
- `merge_tool_responses(responses: list[dict]) -> dict`: Merge tool responses

## Type Definitions

```python
from tantra import (
    AgentConfig,      # Agent configuration TypedDict
    AgentResponse,    # Agent run response TypedDict
    Tool,             # OpenAI tool schema TypedDict
    ToolExecutionResult,  # Tool execution result TypedDict
    Message,          # Chat message TypedDict
)
```

## Examples

See the `examples/` directory for more usage patterns:

- `basic_usage.py`: Simple agent, tools, conversation history, error handling
- `multi_agent.py`: Agent-as-tool pattern, conversation forking, multi-agent coordination

## Future Development

Tantra follows a phased development approach to maintain simplicity while adding powerful features.

### Phase 2: Developer Experience

**Streaming Support**
```python
# Stream responses for better UX with long outputs
async for chunk in agent.stream("Long analysis task..."):
    print(chunk, end="", flush=True)
```

**Retry Logic with Exponential Backoff**
```python
agent = Agent(
    ...,
    retry_attempts=3,        # Retry failed API calls
    retry_delay=1.0,         # Initial delay in seconds
    retry_backoff=2.0        # Exponential backoff multiplier
)
```

**Cost Tracking**
```python
response = await agent.run("Task")
# Automatic cost estimation based on model pricing
print(f"Estimated cost: ${response['usage']['estimated_cost']}")
```

**Message-Level Control**
```python
# Fine-grained control over conversation construction
agent.add_message("user", "First question")
agent.add_message("assistant", "Response")  
agent.add_message("user", "Follow-up")
response = await agent.continue()  # Continue from current state
```

### Phase 3: Advanced Features

**Parallel Agent Execution**
```python
# Run multiple agents in parallel efficiently
results = await Agent.run_parallel([
    (agent1, "Task 1"),
    (agent2, "Task 2"),
    (agent3, "Task 3")
])
```

**Event Hooks for Observability**
```python
# Custom hooks without external dependencies
agent = Agent(
    ...,
    on_tool_start=lambda tool, args: logger.info(f"Starting {tool}"),
    on_tool_end=lambda tool, result: logger.info(f"Completed {tool}"),
    on_llm_start=lambda messages: track_request(messages),
    on_llm_end=lambda response: track_response(response)
)
```

**Prompt Template System** (Optional, stays lightweight)
```python
from tantra import PromptTemplate

template = PromptTemplate("""
You are a {role}.
Your task: {task}
Context: {context}
""")

agent = Agent(
    system_message=template.format(
        role="analyst", 
        task="data analysis", 
        context="Q4 sales data"
    )
)
```

**Community Provider Contributions**
```python
# Community can contribute providers for:
# - Anthropic Claude
# - Google Gemini
# - Ollama (local models)
# - Azure OpenAI
# - Cohere
# - And more...

from tantra import Agent
from tantra_anthropic import AnthropicProvider  # Community package

agent = Agent(
    provider=AnthropicProvider(api_key="..."),
    model="claude-3-opus-20240229"
)
```

### Development Principles

All future features will maintain:
- ✅ **Zero prompt modification** - Pass through exactly what users provide
- ✅ **Full transparency** - Users see everything
- ✅ **No magic** - Explicit over implicit
- ✅ **Lightweight** - Minimal dependencies
- ✅ **Provider agnostic** - Works with any LLM

### Contributing to Roadmap

Have ideas for Tantra? We welcome:
- **Feature proposals** via GitHub Discussions
- **Provider implementations** (Anthropic, Gemini, Ollama, etc.)
- **Performance optimizations**
- **Documentation improvements**
- **Example use cases**

See [Contributing](#contributing) section and [ROADMAP.md](ROADMAP.md) for detailed development plans.

## Requirements

- Python 3.11+
- OpenAI SDK

## Development

```bash
# Clone the repository
git clone https://github.com/axlnet/tantra.git
cd tantra

# Install with poetry
poetry install

# Run examples
python examples/basic_usage.py

# Run tests
pytest

# Format code
black tantra/
ruff check tantra/
```

## Contributing

Contributions welcome! Tantra is designed to be community-driven.

### How to Contribute

1. **Check the [ROADMAP.md](ROADMAP.md)** - See planned features and priorities
2. **Fork the repository** - Create your own copy
3. **Create a feature branch** - Descriptive name for your changes
4. **Add tests** - Ensure new functionality is tested
5. **Update documentation** - README, docstrings, and examples
6. **Ensure all tests pass** - Run `pytest` and linting
7. **Submit a pull request** - Clear description of changes

### Priority Contributions

- **Provider Implementations**: Add support for Anthropic, Gemini, Ollama, etc.
- **Phase 2 Features**: Streaming, retry logic, cost tracking (see ROADMAP.md)
- **Examples**: Real-world multi-agent use cases
- **Documentation**: Tutorials, guides, and better docstrings
- **Performance**: Optimizations that maintain simplicity
- **Vendoring Patterns**: Share your customizations as examples for others (see [VENDORING.md](VENDORING.md))

### Sharing Vendored Customizations

If you've vendored Tantra and made useful modifications:
1. Extract your customization as a pattern
2. Submit a PR to add it to `examples/patterns/`
3. Help others learn from your approach
4. **You keep your vendored code** - just share the pattern!

### Discussion & Ideas

- **New Features**: Open a GitHub Discussion first
- **Bug Reports**: Use GitHub Issues
- **Questions**: GitHub Discussions or Issues

## License

MIT License - see LICENSE file for details

## Why "Tantra"?

Tantra means "framework" or "system" in Sanskrit. Like the philosophical tradition, this framework emphasizes direct experience and practical application over abstract complexity.

## Support

- Issues: https://github.com/axlnet/tantra/issues
- Discussions: https://github.com/axlnet/tantra/discussions

---

Built with transparency by AxlNet
