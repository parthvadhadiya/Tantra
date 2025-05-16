# 🕉️ Tantra

A simple yet powerful agentic AI library that just works.

## Why Tantra?

Most agentic AI frameworks today suffer from two major problems:

1. **High Learning Curve** - Complex architectures, numerous concepts to learn, and extensive setup required
2. **Not Truly Agentic** - Many frameworks claim to be agentic but lack true agency in practice

Tantra solves these problems by providing:

- **Simple API** - Create an agent in just a few lines of code
- **True Agency** - Agents that can actually understand context and maintain state
- **Built for Real Use** - Practical features like parameter collection, memory management, and structured logging

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/tantra.git
cd tantra

# Install using poetry (recommended)
poetry install

# Or install using pip
pip install -e .
```

Create your first agent:

```python
import asyncio
from tantra.agent import Agent
from tantra.tools import Tool
from tantra.session import Session

# Define a simple tool
@Tool
async def set_reminder(task: str, time: str):
    """Set a reminder for a task at a specific time"""
    print(f"Reminder set: {task} at {time}")
    return "Reminder set successfully!"

# Create and run agent
async def main():
    # Create a session with tools
    session = Session(tools=[set_reminder])
    
    # Create an agent with the session
    agent = Agent(session)
    
    # Start the conversation
    await agent.on_event({"type": "SESSION_START"})
    
    # Main conversation loop
    try:
        while True:
            user_input = input("\nYou: ").strip()
            if not user_input:
                break
                
            # Process user input
            await agent.think(user_input)
    except KeyboardInterrupt:
        pass
    
    # End the session gracefully
    await agent.on_event({"type": "SESSION_END"})

# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
```

That's it! Your agent can now:
- Understand natural language requests
- Collect required parameters intelligently
- Remember context and previous interactions
- Execute tools when ready

## Features

### 🧠 Smart Parameter Collection
```python
# User: "set a reminder"
# Agent: "What task would you like to be reminded about?"
# User: "team meeting"
# Agent: "What time should I set the reminder for?"
# User: "tomorrow at 2pm"
# Agent: "I'll set a reminder for your team meeting tomorrow at 2pm"
```

### 📝 Built-in Memory Management
```python
# Agent remembers facts and previous interactions
await agent.memory.add_fact("user_timezone", "EST")
await agent.memory.add_fact("meeting_preference", "mornings")

# Facts influence the agent's decisions
# User: "set a meeting"
# Agent: "Since you prefer mornings, would you like me to schedule it for tomorrow morning?"
```

### 🔍 Structured Logging
```bash
LOG_LEVEL=DEBUG python your_agent.py

# See exactly what's happening:
[2025-05-16 17:51:26] tantra.think - DEBUG - Building prompt with context...
[2025-05-16 17:51:26] tantra.memory - DEBUG - Retrieved parameters: {'task': 'team meeting'}
```

## Installation

1. Make sure you have Python 3.8+ and Poetry installed
2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tantra.git
   cd tantra
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-key-here'
   ```

## Examples

Check out the `examples/` directory for working examples:

### Assistant Agent (`examples/assistant_agent.py`)
```python
# A basic AI assistant that can:
# - Set reminders
# - Search the web
# - Check weather
# - Search vector databases

LOG_LEVEL=DEBUG poetry run python examples/assistant_agent.py
```

### Custom Tool Agent (`examples/custom_tool_agent.py`)
```python
# Shows how to create custom tools and use them with the agent
# Includes examples of:
# - Parameter validation
# - Async tool execution
# - Error handling

poetry run python examples/custom_tool_agent.py
```

## Contributing

We welcome contributions! Some areas we're working on:
- Additional LLM providers
- More built-in tools
- Enhanced memory management
- Better documentation

## License

MIT License - See LICENSE file for details

---

Built with ❤️ by the Tantra team
