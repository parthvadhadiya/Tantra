# Tantra Development Roadmap

This document outlines the planned development phases for Tantra, maintaining our core principles of transparency, simplicity, and developer control.

## Core Principles

All future development will adhere to:

- ✅ **Zero Prompt Modification** - Never alter user prompts
- ✅ **Full Transparency** - Complete visibility into operations
- ✅ **No Magic** - Explicit behavior, no hidden state
- ✅ **Lightweight** - Minimal core dependencies
- ✅ **Vendorable by Design** - Code designed to be copied and customized
- ✅ **Provider Agnostic** - Works with any LLM backend
- ✅ **Backward Compatible** - Preserve existing functionality

### Vendoring Philosophy

Tantra supports **two first-class usage patterns**:

1. **Traditional Install**: `pip install tantra` - for prototyping
2. **Vendor into Project**: `cp -r tantra/ myproject/` - for full control

This dual approach means all code must be:
- Simple enough to read and understand (~1200 lines core)
- Well-documented for modification
- Self-contained without complex dependencies
- Stable to minimize breaking changes for vendored users

**Future features must maintain vendorability.**

---

## Phase 1: Core Multi-Agent ✅ **COMPLETED**

**Goal**: Enable powerful multi-agent systems with minimal abstraction.

### Completed Features

- ✅ **LLM Provider Abstraction**
  - Abstract `LLMProvider` base class
  - `OpenAIProvider` implementation
  - Standardized response format
  - Community extensible for Anthropic, Gemini, Ollama, etc.

- ✅ **Agent-as-Tool Pattern**
  - `agent.as_tool()` method
  - Agents can use other agents as specialized tools
  - Automatic conversation forking when used as tools
  - Enables hierarchical multi-agent systems

- ✅ **Conversation Forking**
  - `agent.fork()` method
  - Deep copy of conversation state
  - Enables multi-path exploration
  - Perfect for A/B testing approaches

- ✅ **Usage Tracking**
  - Token counting across all API calls
  - `response['usage']` with prompt/completion/total tokens
  - Foundation for cost tracking

---

## Phase 2: Developer Experience 🔄 **PLANNED**

**Goal**: Make Tantra more ergonomic and production-ready while staying lightweight.

### Streaming Support

**Why**: Improve UX for long-running tasks with real-time feedback

```python
# Proposed API
async for chunk in agent.stream("Long analysis task..."):
    print(chunk, end="", flush=True)
```

**Implementation Notes**:
- Add `async stream(task: str)` method to Agent
- Yield content chunks as they arrive from LLM
- Maintain full conversation history like `run()` does
- Return final `AgentResponse` when complete

**Considerations**:
- Handle tool calls in streaming mode
- Decide behavior: stream tool execution or only final response?
- Update provider interface to support streaming

---

### Retry Logic with Exponential Backoff

**Why**: Handle transient API failures gracefully

```python
# Proposed API
agent = Agent(
    ...,
    retry_attempts=3,        # Number of retry attempts
    retry_delay=1.0,         # Initial delay in seconds
    retry_backoff=2.0        # Exponential backoff multiplier
)
```

**Implementation Notes**:
- Add retry configuration to `Agent.__init__()`
- Implement in `_call_openai()` method
- Use asyncio.sleep for delays
- Log retry attempts at INFO level
- Make configurable per-agent

**Considerations**:
- Which errors to retry? (rate limits, timeouts, 5xx errors)
- Max total retry time?
- Exponential backoff with jitter?

---

### Cost Tracking

**Why**: Help users monitor and control LLM costs

```python
# Proposed API
response = await agent.run("Task")
print(f"Cost: ${response['usage']['estimated_cost']}")
```

**Implementation Notes**:
- Add pricing data for common models
- Calculate cost from token usage
- Include in `usage` dict
- Support cost estimation across providers

**Considerations**:
- Keep pricing data updated
- Handle custom/fine-tuned models
- Provider-specific pricing?

---

### Message-Level Control

**Why**: Enable fine-grained conversation building for advanced use cases

```python
# Proposed API
agent.add_message("user", "Question 1")
agent.add_message("assistant", "Answer 1")  
agent.add_message("user", "Question 2")
response = await agent.continue()  # Continue from current state
```

**Implementation Notes**:
- Add `add_message(role: str, content: str)` method
- Add `continue()` method (like `run` but no initial system/user message)
- Maintain backward compatibility with `run()`

**Considerations**:
- Validation of message sequences?
- How to handle system messages?
- Should `continue()` support tool calling?

---

## Phase 3: Advanced Features 🔮 **FUTURE**

**Goal**: Enable sophisticated agent architectures and workflows.

### Parallel Agent Execution

**Why**: Run multiple independent agents efficiently

```python
# Proposed API
results = await Agent.run_parallel([
    (agent1, "Task 1"),
    (agent2, "Task 2"),
    (agent3, "Task 3")
])
```

**Implementation Notes**:
- Add static method to Agent class
- Use `asyncio.gather()` internally
- Handle partial failures gracefully
- Return list of `AgentResponse` objects

**Considerations**:
- Error handling strategy?
- Should it fork agents automatically?
- Progress tracking?

---

### Event Hooks for Observability

**Why**: Custom observability without external dependencies

```python
# Proposed API
def on_tool_start(tool_name: str, arguments: dict):
    logger.info(f"Starting {tool_name}")
    
agent = Agent(
    ...,
    on_tool_start=on_tool_start,
    on_tool_end=lambda tool, result: metrics.record(tool, result),
    on_llm_start=lambda messages: track_request(messages),
    on_llm_end=lambda response: track_response(response)
)
```

**Implementation Notes**:
- Add optional callback parameters to `Agent.__init__()`
- Call hooks at appropriate points in execution
- Make all hooks optional
- Pass relevant context to each hook

**Considerations**:
- Should hooks be async or sync?
- Error handling in hooks?
- Performance impact?

---

### Prompt Template System

**Why**: Help users organize and reuse prompts (optional feature)

```python
# Proposed API
from tantra import PromptTemplate

template = PromptTemplate("""
You are a {role}.
Your task: {task}
Context: {context}
""")

agent = Agent(
    system_message=template.format(
        role="analyst", 
        task="analyze data",
        context="Q4 sales"
    )
)
```

**Implementation Notes**:
- Simple variable substitution class
- No complex templating engine (keep it simple)
- Purely optional - doesn't affect core functionality

**Considerations**:
- Is this needed or too much?
- Could users just use f-strings?
- Add validation for required variables?

---

### Community Provider Ecosystem

**Why**: Support diverse LLM backends through community contributions

**Target Providers**:
- Anthropic Claude (`tantra-anthropic`)
- Google Gemini (`tantra-gemini`)
- Ollama (local models) (`tantra-ollama`)
- Azure OpenAI (`tantra-azure`)
- Cohere (`tantra-cohere`)
- AWS Bedrock (`tantra-bedrock`)

**Implementation Notes**:
- Document provider implementation guide
- Create template/example provider
- Establish testing requirements
- Set up community package structure

**Considerations**:
- Separate repos or monorepo?
- How to discover community providers?
- Quality standards for official endorsement?

---

## Contributing to Roadmap

We welcome community input on:

- **Feature Priorities**: Which Phase 2/3 features are most important?
- **New Ideas**: What else would make Tantra more useful?
- **Provider Implementations**: Help add support for new LLMs
- **Performance**: Optimizations that maintain simplicity
- **Documentation**: Better examples and guides

### How to Contribute

1. **Discuss First**: Open a GitHub Discussion for new ideas
2. **Check Issues**: See if feature is already planned
3. **Propose API**: Show example usage in your proposal
4. **Consider Principles**: Does it maintain transparency and simplicity?
5. **Submit PR**: Include tests, docs, and examples

---

## Timeline

**Phase 1**: ✅ Completed (Current)

**Phase 2**: Target 2-3 features per release
- Streaming Support: High priority
- Retry Logic: High priority  
- Cost Tracking: Medium priority
- Message Control: Medium priority

**Phase 3**: Community-driven timing
- Based on user feedback and requests
- Implemented as optional features
- Maintains backward compatibility

---

## Decision Log

### Why Phase 1 First?

Multi-agent capabilities are fundamental to Tantra's value proposition. Provider abstraction enables the community to extend support to any LLM.

### Why Not Add Everything at Once?

Incremental development:
1. Validates each feature with real usage
2. Maintains code quality and test coverage
3. Allows for community feedback
4. Prevents feature bloat

### Why These Specific Phases?

- **Phase 1**: Foundation for multi-agent systems (most unique value)
- **Phase 2**: Production readiness (streaming, retry, cost)
- **Phase 3**: Advanced patterns (nice-to-have, optional)

---

## Questions or Suggestions?

- **GitHub Discussions**: https://github.com/axlnet/tantra/discussions
- **Issues**: https://github.com/axlnet/tantra/issues

Let's build the most transparent, developer-friendly LLM framework together! 🚀
