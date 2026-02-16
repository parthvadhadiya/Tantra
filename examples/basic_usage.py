"""
Example usage of the Tantra framework.

This demonstrates basic usage patterns.
"""
import asyncio
from tantra import Agent, extract_json_from_response


# Example 1: Simple agent with no tools
async def example_simple_agent():
    """Simple agent without tools - just conversation."""
    agent = Agent(
        name="Summarizer",
        system_message="You are a concise summarizer. Provide brief, accurate summaries.",
        model="gpt-4o",
        temperature=0.0
    )

    response = await agent.run("Explain what an LLM agent is in 2 sentences.")

    print("Response:", response['content'])
    print("Success:", response['success'])
    print("Iterations:", response['iterations'])


# Example 2: Agent with tools
async def fetch_weather(city: str) -> dict:
    """
    Fetch weather data for a city.

    Args:
        city: City name

    Returns:
        Weather data dictionary
    """
    # Simulate weather API
    return {
        "city": city,
        "temperature": 72,
        "condition": "Sunny",
        "humidity": 45
    }


async def fetch_news(topic: str, limit: int = 5) -> dict:
    """
    Fetch news articles about a topic.

    Args:
        topic: News topic to search for
        limit: Maximum number of articles to return

    Returns:
        Dictionary with articles list
    """
    # Simulate news API
    return {
        "articles": [
            {"title": f"Breaking: {topic} developments", "url": "https://..."},
            {"title": f"Analysis: The future of {topic}", "url": "https://..."}
        ]
    }


async def example_agent_with_tools():
    """Agent with tools - function calling."""
    agent = Agent(
        name="Research_Assistant",
        system_message="""You are a research assistant.

        When asked about a city, you MUST:
        1. Call fetch_weather to get weather info
        2. Call fetch_news to get recent news
        3. Provide a comprehensive summary

        Return your analysis as JSON with:
        {
            "city": "...",
            "weather_summary": "...",
            "news_count": ...
        }
        """,
        tools=[fetch_weather, fetch_news],
        model="gpt-4o",
        tool_choice="auto"
    )

    response = await agent.run("Tell me about San Francisco")

    print("\nAgent Response:")
    print("Success:", response['success'])
    print("Iterations:", response['iterations'])
    print("Tools Called:", len(response['tool_calls']))

    for tool_call in response['tool_calls']:
        print(f"  - {tool_call['tool']}: success={tool_call['success']}")

    # Extract JSON from response
    json_data = extract_json_from_response(response['content'])
    if json_data:
        print("\nExtracted JSON:")
        print(json_data)


# Example 3: Conversation history access
async def example_conversation_history():
    """Access full conversation history for debugging/logging."""
    agent = Agent(
        name="Analyzer",
        system_message="You are a helpful analyst.",
        tools=[fetch_weather],
        model="gpt-4o"
    )

    response = await agent.run("Get weather for Tokyo and summarize it")

    print("\nFull Conversation History:")
    for i, msg in enumerate(agent.get_messages()):
        print(f"\nMessage {i+1} ({msg['role']}):")
        if msg.get('content'):
            print(f"  Content: {msg['content'][:100]}...")
        if msg.get('tool_calls'):
            print(f"  Tool Calls: {len(msg['tool_calls'])}")


# Example 4: Error handling
async def example_error_handling():
    """Demonstrate error handling."""

    async def failing_tool(param: str) -> dict:
        """A tool that fails."""
        raise ValueError("Simulated tool error")

    agent = Agent(
        name="TestAgent",
        system_message="Call the failing_tool.",
        tools=[failing_tool],
        model="gpt-4o"
    )

    response = await agent.run("Use the failing tool with param='test'")

    print("\nError Handling:")
    print("Success:", response['success'])
    print("Error:", response['error'])
    print("Tool Calls:", response['tool_calls'])


async def main():
    """Run all examples."""
    print("="*60)
    print("Example 1: Simple Agent")
    print("="*60)
    await example_simple_agent()

    print("\n" + "="*60)
    print("Example 2: Agent with Tools")
    print("="*60)
    await example_agent_with_tools()

    print("\n" + "="*60)
    print("Example 3: Conversation History")
    print("="*60)
    await example_conversation_history()

    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)
    await example_error_handling()


if __name__ == "__main__":
    asyncio.run(main())
