# GitHub Copilot Instructions for Tantra

## Project Overview

**Tantra** is a clean, transparent LLM framework for building multi-agent systems with OpenAI and other LLM providers. It provides straightforward agent orchestration without framework magic, giving developers full visibility into every API call and tool execution.

### Core Philosophy

- **No Magic**: Explicit conversation state, tool schemas auto-generated from code
- **Full Transparency**: Complete access to conversation history, tool calls, and iterations
- **Vendorable by Design**: Code is designed to be copied into user projects for full control
- **Provider Agnostic**: Lightweight provider abstraction (OpenAI supported, community can add others)
- **Multi-Agent Ready**: Agent-as-tool pattern and conversation forking for complex agent systems
- **Async-First**: All operations use async/await for performance
- **Simple & Powerful**: Clean API that doesn't hide complexity

### Vendoring Philosophy

Tantra is designed for **hybrid usage**:

1. **Traditional Install**: `pip install tantra` - for quick prototyping
2. **Vendor into Project**: `cp -r tantra/ myproject/` - for full control and customization

This means:
- ✅ **Keep code simple and readable** - users will read and modify it
- ✅ **Avoid complex abstractions** - users need to understand every line
- ✅ **Self-contained modules** - easy to copy parts
- ✅ **Well-documented** - vendored code needs clear docs
- ✅ **Minimal dependencies** - only OpenAI SDK required
- ✅ **Stable interfaces** - breaking changes hurt vendored users

**When writing code, assume users will read, copy, and modify it. This is a feature, not a bug.**

### Code Size

Core codebase: ~1200 lines (including docstrings)
- agent.py: ~480 lines
- tools.py: ~260 lines  
- utils.py: ~160 lines
- providers.py: ~150 lines
- types.py: ~70 lines
- __init__.py: ~70 lines

Keep additions minimal and well-justified.

## Project Structure

```
tantra/
├── __init__.py       # Public API exports
├── agent.py          # Core Agent class with multi-agent support
├── providers.py      # LLM provider abstraction layer
├── tools.py          # Tool schema generation and execution
├── types.py          # TypedDict definitions for all data structures
└── utils.py          # Utility functions (JSON/HTML extraction, formatting)

examples/
├── basic_usage.py    # Basic agent usage examples
└── multi_agent.py    # Multi-agent patterns and coordination

pyproject.toml        # Poetry configuration, dependencies, dev tools
README.md             # Complete documentation
```

## Architecture & Key Modules

### 1. Agent (`agent.py`)

**Purpose**: Core orchestrator for LLM conversations with tool calling and multi-agent support.

**Key Responsibilities**:
- Manages conversation state (messages list)
- Handles LLM API calls via provider abstraction
- Executes tool calling loop with iteration limits
- Provides conversation history management
- Supports agent-as-tool pattern for multi-agent systems
- Enables conversation forking for multi-path exploration
- Tracks token usage

**Important Methods**:
- `__init__()`: Configure agent with system message, tools, model, provider, parameters
- `async run(task: str)`: Main execution loop returning AgentResponse
- `fork()`: Create a copy of agent with duplicated conversation state
- `as_tool()`: Convert agent to a callable tool for use by other agents
- `reset()`: Clear conversation history
- `get_messages()`: Return copy of conversation history
- `add_user_message()`: Manually add user messages
- `_call_openai()`: Internal LLM provider call (now provider-agnostic)
- `_message_to_dict()`: Convert message objects to dict

**Key Patterns**:
- Tool schemas generated once during initialization
- Iteration loop continues until `finish_reason == "stop"` or max iterations
- All tool results added to messages as `role: "tool"`
- Truncation of tool results optional (controlled by `truncate_tool_results`)
- Usage tracking accumulated across all API calls

### 2. Providers (`providers.py`)

**Purpose**: Lightweight abstraction layer for different LLM providers.

**Key Classes**:
- `LLMProvider`: Abstract base class defining provider interface
  - `async create_completion()`: Standard method all providers must implement
  - Returns standardized response format
  
- `OpenAIProvider`: OpenAI implementation
  - Uses AsyncOpenAI client
  - Handles tool calling in OpenAI format
  - Tracks token usage
  - Converts to standardized response format

**Design Principles**:
- Minimal abstraction - just enough to swap providers
- Community extensible - easy to add Anthropic, Gemini, Ollama, etc.
- Standardized response format for interoperability
- No hidden transformations

**Adding New Providers**:
Contributors should implement `LLMProvider` interface:
```python
class CustomProvider(LLMProvider):
    async def create_completion(self, messages, model, **kwargs):
        # Call your LLM API
        # Return standardized format
        return {
            "message": {"role": "assistant", "content": "...", "tool_calls": [...]},
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
```

### 3. Tools (`tools.py`)

**Purpose**: Automatic tool schema generation and execution utilities.

**Key Functions**:
- `generate_tool_schema(func)`: Auto-generate OpenAI tool schema from Python function
  - Extracts type hints, signature, and docstring
  - Parses Google-style docstrings for parameter descriptions
  - Handles both sync and async functions
  - Required parameters identified by absence of default values
  
- `execute_tool(func, arguments)`: Execute tool with error handling
  - Handles both sync and async functions
  - Returns ToolExecutionResult with success/error info
  - JSON serializes results
  
- `format_tool_result(result, max_length)`: Format and truncate tool output
  - JSON serialization of complex objects
  - Configurable truncation for large outputs

**Schema Generation Rules**:
- Function name becomes tool name
- First line of docstring becomes function description
- Type hints mapped to JSON schema types: `str → "string"`, `int → "integer"`, etc.
- Google-style docstring Args section parsed for parameter descriptions
- Parameters with defaults are optional; without defaults are required

### 3. Types (`types.py`)

**Purpose**: Comprehensive TypedDict definitions for type safety.

**Key Types**:
- `AgentConfig`: Agent initialization configuration
- `AgentResponse`: Complete response from agent.run() including success, content, messages, tool_calls, iterations, error
- `Message`: Chat message with role, content, tool_calls, tool_call_id
- `Tool`: OpenAI tool schema structure
- `ToolFunction`: Function definition within tool
- `ToolParameter`: Parameter definition for tools
- `ToolExecutionResult`: Result of tool execution with success/error
- `AsyncToolFunction`, `SyncToolFunction`: Type aliases for tool functions

**Usage Pattern**: Import types for function signatures and return types to maintain type safety throughout codebase.

### 4. Utils (`utils.py`)

**Purpose**: Utility functions for response parsing and formatting.

**Key Functions**:
- `extract_json_from_response(text)`: Extract JSON from various formats (pure JSON, markdown blocks, embedded JSON)
- `extract_html_from_response(text)`: Extract HTML from response text
- `truncate_for_logging(text, max_length)`: Truncate with ellipsis
- `count_tokens_estimate(text)`: Rough token estimation (~4 chars/token)
- `format_error_for_display(error)`: User-friendly error formatting
- `merge_tool_responses(responses)`: Combine multiple tool results

## Code Conventions

### Type Annotations

- **Always use type hints** for all function parameters and return values
- Use `Optional[T]` for nullable values
- Use `list[T]` and `dict[K, V]` (Python 3.11+ syntax, not `List`, `Dict`)
- Union types with `|` operator: `str | int` not `Union[str, int]`

### Docstrings

**Format**: Google-style docstrings consistently throughout

```python
async def function_name(param1: str, param2: int = 10) -> dict:
    """
    Brief description of function (single line).

    Optional longer description with more details about behavior,
    edge cases, or implementation notes.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value structure

    Example:
        >>> result = await function_name("test", 5)
        >>> result['key']
        'value'
    """
```

### Async/Await

- **Prefer async** for all I/O operations (OpenAI API, tool execution)
- Tool functions can be sync or async - framework handles both
- Use `asyncio.iscoroutinefunction()` to detect async functions
- Always `await` async function calls

### Error Handling

- Use try/except blocks for tool execution
- Return structured error information in ToolExecutionResult
- Log errors with appropriate level (error, warning, debug)
- Don't fail silently - propagate errors to agent response

### Logging

- Use Python's `logging` module
- Logger instance: `logger = logging.getLogger(__name__)`
- Levels: DEBUG for detailed info, INFO for workflow, ERROR for failures
- Include agent name in log messages: `f"[{self.name}] Message"`

## Tool Creation Guidelines

When creating tools for Tantra agents:

### 1. Function Signature

```python
async def tool_name(param1: str, param2: int = 5) -> dict:
    """Tool description for schema."""
```

- Use descriptive names (snake_case)
- Include type hints for all parameters
- Return dict or simple types (str, int, bool, list, dict)
- Async recommended for I/O operations

### 2. Docstring Requirements

```python
"""
Brief description (becomes function description in schema).

Args:
    param1: Description of what param1 represents
    param2: Description with context about param2

Returns:
    Description of return value structure
"""
```

- First line is critical - becomes OpenAI function description
- Args section parsed for parameter descriptions
- Clear, concise parameter descriptions help LLM use tools correctly

### 3. Return Values

- Return structured data (preferably dict)
- JSON-serializable values only
- Avoid returning large binary data
- Consider truncation for large results

### 4. Error Handling

```python
async def tool_with_error_handling(param: str) -> dict:
    """Tool description."""
    try:
        result = await some_api_call(param)
        return {"status": "success", "data": result}
    except Exception as e:
        # Let framework handle errors, or return structured error
        return {"status": "error", "message": str(e)}
```

## Agent Usage Patterns

### Basic Agent (No Tools)

```python
agent = Agent(
    name="AgentName",
    system_message="You are a helpful assistant...",
    model="gpt-4o",
    temperature=0.0
)

response = await agent.run("User task")
print(response['content'])
```

### Agent with Tools

```python
async def custom_tool(param: str) -> dict:
    """Tool description."""
    return {"result": "..."}

agent = Agent(
    name="AgentName",
    system_message="System prompt with tool usage instructions...",
    tools=[custom_tool, another_tool],
    model="gpt-4o",
    tool_choice="auto",  # or "required" or "none"
    max_iterations=20,
    truncate_tool_results=True
)

response = await agent.run("Task requiring tools")
```

### Response Structure

```python
{
    "success": bool,              # Execution success status
    "content": str | None,        # Final agent response text
    "messages": list[Message],    # Full conversation history
    "tool_calls": list[dict],     # All tool calls made
    "iterations": int,            # Number of iterations taken
    "usage": dict[str, int],      # Token usage (prompt, completion, total)
    "error": str | None          # Error message if failed
}
```

### Conversation Management

```python
# Access messages
messages = agent.get_messages()

# Reset conversation
agent.reset()

# Add manual message
agent.add_user_message("Additional context")

# Get last response
last = agent.get_last_response()
```

## Multi-Agent Patterns

### Agent-as-Tool

Enable one agent to use another agent as a tool for specialized tasks:

```python
# Create specialized agents
researcher = Agent(
    name="Researcher",
    system_message="You research topics thoroughly.",
    model="gpt-4o"
)

writer = Agent(
    name="Writer",
    system_message="You write engaging content.",
    model="gpt-4o"
)

# Coordinator uses agents as tools
coordinator = Agent(
    name="Coordinator",
    system_message="You coordinate research and writing.",
    tools=[
        researcher.as_tool(),  # Convert agent to tool
        writer.as_tool()
    ],
    model="gpt-4o"
)

# Coordinator delegates to specialized agents
response = await coordinator.run("Create article about AI")
```

### Conversation Forking

Fork agent state to explore multiple conversation paths:

```python
agent = Agent(name="Analyst", ...)
await agent.run("Initial analysis")

# Fork to explore different approaches
fork1 = agent.fork()  # Independent copy of conversation
fork2 = agent.fork()

# Explore in parallel
results = await asyncio.gather(
    fork1.run("Approach A"),
    fork2.run("Approach B")
)

# Original agent state unchanged
```

### Multi-Level Coordination

Build complex agent hierarchies:

```python
# Level 1: Specialized agents
data_agent = Agent(name="Data", ...)
research_agent = Agent(name="Research", ...)

# Level 2: Department coordinators  
tech_coordinator = Agent(
    name="Tech",
    tools=[data_agent.as_tool(), research_agent.as_tool()],
    ...
)

# Level 3: Master coordinator
master = Agent(
    name="Master",
    tools=[tech_coordinator.as_tool()],
    ...
)
```

### Usage Tracking

Access token usage for cost monitoring:

```python
response = await agent.run("Task")

print(f"Tokens used: {response['usage']['total_tokens']}")
print(f"Prompt: {response['usage']['prompt_tokens']}")
print(f"Completion: {response['usage']['completion_tokens']}")
```

## Dependencies

### Production
- **openai**: `^1.0.0` - OpenAI Python SDK for API calls
- **python**: `^3.11` - Modern Python features (type unions, etc.)

### Development
- **pytest**: Testing framework (with pytest-asyncio)
- **black**: Code formatting (line-length=100)
- **ruff**: Linting (E, F, I, W rules)
- **mypy**: Static type checking

## Testing Guidelines

- Use pytest with pytest-asyncio for async test support
- Test both sync and async tool functions
- Mock OpenAI API calls in tests
- Test error conditions and edge cases
- Verify tool schema generation accuracy

## Code Style

### Formatting
- **Line length**: 100 characters (enforced by black and ruff)
- **Quotes**: Prefer double quotes for strings
- **Indentation**: 4 spaces
- **Imports**: Organized by standard lib, third-party, local (ruff enforces)

### Naming
- **Classes**: PascalCase (e.g., `Agent`, `ToolExecutionResult`)
- **Functions/Methods**: snake_case (e.g., `generate_tool_schema`, `execute_tool`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_ITERATIONS`)
- **Private methods**: Leading underscore (e.g., `_call_openai`)

## Important Implementation Notes

### Agent Execution Loop

1. Initialize messages with system message and user task
2. Loop until max_iterations:
   - Call OpenAI API with current messages and tool schemas
   - Add assistant message to history
   - If finish_reason is "stop" or no tool_calls, return response
   - If tool_calls present, execute each tool
   - Add tool results to messages as role="tool"
   - Continue loop
3. If max_iterations reached, return with error

### Tool Schema Generation

- Inspects function signature using `inspect.signature()`
- Gets type hints via `get_type_hints()`
- Parses docstring for descriptions
- Maps Python types to JSON schema types
- Handles required vs optional parameters
- Stores tool function in `tool_map` for execution

### Message Format

System message:
```python
{"role": "system", "content": "System prompt"}
```

User message:
```python
{"role": "user", "content": "User input"}
```

Assistant message (with tool calls):
```python
{
    "role": "assistant",
    "content": None,
    "tool_calls": [{"id": "...", "function": {"name": "...", "arguments": "..."}}]
}
```

Tool response:
```python
{"role": "tool", "tool_call_id": "...", "content": "Tool result"}
```

## Common Patterns to Suggest

### 1. Creating a new tool
```python
async def new_tool(required_param: str, optional_param: int = 10) -> dict:
    """
    Brief description of what this tool does.

    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter

    Returns:
        Dictionary with tool results
    """
    # Implementation
    return {"result": "..."}
```

### 2. Extracting structured data from agent response
```python
from tantra import extract_json_from_response

response = await agent.run("Return JSON with fields...")
data = extract_json_from_response(response['content'])
```

### 3. Error handling in agent usage
```python
response = await agent.run("Task")

if not response['success']:
    print(f"Error: {response['error']}")
    
    # Check individual tool failures
    for tool_call in response['tool_calls']:
        if not tool_call['success']:
            print(f"Tool {tool_call['tool']} failed: {tool_call['error']}")
```

### 4. Multi-step conversation
```python
agent = Agent(...)

# First interaction
response1 = await agent.run("Initial task")

# Agent remembers context - conversation continues
response2 = await agent.run("Follow-up task based on previous")

# Access full history
full_conversation = agent.get_messages()
```

## When Suggesting Code

1. **Always use async/await** for Agent operations and I/O
2. **Include type hints** for parameters and return values
3. **Add Google-style docstrings** for new functions
4. **Follow the established patterns** from existing code
5. **Don't add unnecessary abstractions** - keep it simple and transparent
6. **Ensure JSON serializability** for tool returns
7. **Use descriptive names** that clarify intent
8. **Handle errors gracefully** with try/except where appropriate
9. **Log appropriately** for observability
10. **Keep tool functions focused** - one clear purpose per tool

## Anti-Patterns to Avoid

- ❌ Hiding state or API calls behind abstractions
- ❌ Using sync code for I/O operations
- ❌ Omitting type hints or docstrings
- ❌ Returning non-serializable objects from tools
- ❌ Creating tools that do too many things
- ❌ Ignoring errors or failing silently
- ❌ Using old-style type hints (`List`, `Dict` instead of `list`, `dict`)
- ❌ Overly complex tool schemas or parameters
- ❌ Not providing clear docstrings for tool functions

## Future Development Roadmap

### Phase 1: Core Multi-Agent ✅ (Completed)
1. ✅ **LLM Provider abstraction** - Extensible provider interface
2. ✅ **Agent-as-Tool pattern** - Multi-agent coordination
3. ✅ **Conversation forking** - Multi-path exploration
4. ✅ **Usage tracking** - Token counting across API calls

### Phase 2: Developer Experience (Planned)

**Streaming Support**
- Add `async stream(task: str)` method to Agent
- Yield chunks as they arrive from LLM
- Maintain compatibility with existing `run()` method

**Retry Logic**
- Add retry configuration to Agent constructor
- Implement exponential backoff for failed API calls
- Make retry behavior configurable per agent

**Cost Tracking**
- Add cost estimation based on model pricing
- Include in `usage` dict: `estimated_cost`
- Support cost tracking across provider implementations

**Message-Level Control**
- Add `add_message(role, content)` for manual message construction
- Add `continue()` method to resume from current state
- Enable fine-grained conversation building

### Phase 3: Advanced Features (Planned)

**Parallel Agent Execution**
- Static method `Agent.run_parallel(agent_task_pairs)`
- Efficient concurrent execution with proper error handling
- Return aggregated results

**Event Hooks**
- Add optional callback parameters to Agent constructor
- `on_tool_start`, `on_tool_end`, `on_llm_start`, `on_llm_end`
- Enable custom observability without dependencies

**Prompt Template System**
- Optional `PromptTemplate` class for managing prompts
- Simple variable substitution
- Helps users organize and reuse prompts

**Community Provider Ecosystem**
- Document provider implementation guide
- Encourage community to add:
  - Anthropic Claude
  - Google Gemini
  - Ollama (local models)
  - Azure OpenAI
  - Cohere
  - Others...

### Design Principles for All Future Features

- ✅ **No prompt modification** - Never alter user's exact prompts
- ✅ **Full transparency** - Everything visible to developers
- ✅ **No magic** - Explicit behavior, no hidden state
- ✅ **Lightweight** - Minimal core dependencies
- ✅ **Provider agnostic** - Works with any LLM backend
- ✅ **Backward compatible** - Don't break existing code

### Implementation Guidelines for Future Features

When implementing roadmap features:

1. **Start with types** - Define TypedDicts in `types.py` first
2. **Write tests** - Test-driven development for reliability
3. **Document thoroughly** - Update README and copilot instructions
4. **Add examples** - Show real usage in `examples/`
5. **Maintain simplicity** - Avoid over-engineering
6. **Keep it optional** - New features shouldn't complicate basic usage
7. **Benchmark performance** - Ensure no regression

## Repository Metadata

- **License**: MIT
- **Python Versions**: 3.11+
- **Author**: AxlNet
- **Repository**: https://github.com/axlnet/tantra
- **Package Manager**: Poetry
- **Primary Use Case**: Building transparent LLM agents with OpenAI function calling

---

**When working in this codebase, prioritize transparency, simplicity, and type safety. Every abstraction should have a clear purpose, and developers should always be able to see exactly what's happening under the hood.**
