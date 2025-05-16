import asyncio
import os
from typing import Optional, Required
from tantra.agent import Agent
from tantra.tools import tool
from tantra.session import Session

# Tool definitions
@tool(description="Search the web for information")
async def web_search(query: Required[str]) -> str:
    """Simulated web search tool"""
    return f"Found results for: {query}"

@tool(description="Search vector database for relevant documents")
async def vector_search(query: Required[str], limit: Optional[int] = 3) -> str:
    """Simulated vector database search"""
    return f"Found {limit} documents matching: {query}"

@tool(description="Get current weather for a location")
async def get_weather(location: Required[str], unit: Optional[str] = "F") -> str:
    """Simulated weather information"""
    return f"Weather in {location}: Sunny, 72°{unit}"

@tool(description="Set a reminder")
async def set_reminder(task: Required[str], time: Required[str]) -> str:
    """Simulated reminder setting"""
    return f"Reminder set: {task} at {time}"

class AssistantAgent(Agent):
    """An AI assistant that can use multiple tools to help users"""
    
    def __init__(self, **kwargs):
        # Configure the agent
        config = {
            "name": kwargs.get("name", "Assistant"),
            "instructions": """I am an AI assistant that can help with various tasks using tools.
            I can search the web, look up documents, check weather, and set reminders.
            I aim to be helpful and informative.
            When using tools, format your response as @tool_name(arg1='value1', arg2='value2').""",
            "llm_type": kwargs.get("llm_type"),
            "llm_model": kwargs.get("llm_model"),
            "llm_api_key": kwargs.get("llm_api_key"),
            "llm_options": kwargs.get("llm_options", {}),
            "streaming": kwargs.get("streaming", True)
        }
        
        # Initialize parent Agent class
        super().__init__(config)
        
        # Register tools
        self.register_tool(web_search)
        self.register_tool(vector_search)
        self.register_tool(get_weather)
        self.register_tool(set_reminder)
    
    async def on_enter(self) -> Optional[str]:
        """Called when agent starts a new session"""
        tools = self.tools.get_tool_descriptions()
        return f"""Hello! I'm {self.name}, your AI assistant. I can help you with various tasks using these tools:

{tools}

How can I assist you today?"""
    
    async def on_exit(self) -> Optional[str]:
        """Called when agent ends a session"""
        return "Goodbye! Feel free to return if you need any more assistance. Have a great day!"

async def main():
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found! Set it in your environment:"
            "\n\texport OPENAI_API_KEY='your-key-here'"
        )

    # Create agent with configuration
    agent = AssistantAgent(
        name="Alex",  # Agent name
        llm_type="openai",  # Using OpenAI
        llm_model="gpt-4o",  # Model to use
        llm_api_key=api_key,  # API key
        llm_options={
            "temperature": 0.7,  # More creative
            "max_tokens": 150  # Reasonable response length
        },
        streaming=False  # Enable streaming responses
    )
    
    # Create and attach session
    Session(agent)  # Session is stored in agent.session
    

    # Start session
    await agent.on_event({"type": "SESSION_START"})
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            if user_input.lower() == "exit":
                # End session gracefully
                await agent.on_event({"type": "SESSION_END"})
                break
                
            # Get agent's response
            response = await agent.on_event({"type": "USER_MESSAGE", "content": user_input})
            if response:  # Only print if there's a response
                print("\nAssistant:", response)
            
        except KeyboardInterrupt:
            # End session gracefully on Ctrl+C
            await agent.on_event({"type": "SESSION_END"})
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            # End session with error
            await agent.on_event({"type": "SESSION_END"})
            break

if __name__ == "__main__":
    asyncio.run(main())
