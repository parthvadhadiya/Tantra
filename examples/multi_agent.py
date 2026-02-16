"""
Multi-Agent examples demonstrating Tantra's Phase 1 features.

Shows agent-as-tool pattern, conversation forking, and multi-agent coordination.
"""
import asyncio

from tantra import Agent


# Example 1: Agent-as-Tool Pattern (Multi-Agent Coordination)
async def example_agent_as_tool():
    """Demonstrate using agents as tools for other agents."""
    
    # Create specialized agents
    researcher = Agent(
        name="Researcher",
        system_message="""You are a research specialist. When given a topic,
        you provide detailed, factual research findings.""",
        model="gpt-4o"
    )
    
    writer = Agent(
        name="Writer",
        system_message="""You are a creative writer. When given information,
        you write engaging, well-structured articles.""",
        model="gpt-4o"
    )
    
    # Coordinator agent that uses other agents as tools
    coordinator = Agent(
        name="Coordinator",
        system_message="""You are a project coordinator. You have access to:
        - researcher: For gathering factual information
        - writer: For creating engaging content
        
        Use these agents to complete tasks efficiently.""",
        tools=[
            researcher.as_tool(description="Research topics and gather factual information"),
            writer.as_tool(description="Write engaging articles based on information")
        ],
        model="gpt-4o"
    )
    
    # The coordinator will automatically delegate to specialized agents
    response = await coordinator.run("""
    Create a short article about quantum computing.
    First research the topic, then write an engaging article.
    """)
    
    print("=== Agent-as-Tool Coordination ===")
    print(f"Success: {response['success']}")
    print(f"Tools used: {len(response['tool_calls'])}")
    print(f"\nFinal article:\n{response['content']}")
    print(f"\nUsage: {response['usage']}")


# Example 2: Conversation Forking (Multi-Path Exploration)
async def example_conversation_forking():
    """Demonstrate forking conversations to explore different approaches."""
    
    analyst = Agent(
        name="DataAnalyst",
        system_message="You are a data analyst. Analyze data and provide insights.",
        model="gpt-4o"
    )
    
    # Initial analysis
    initial = await analyst.run("""
    We have sales data showing a 20% increase in Q4.
    What could be the contributing factors?
    """)
    
    print("\n=== Conversation Forking ===")
    print(f"Initial analysis: {initial['content'][:200]}...\n")
    
    # Fork the conversation to explore different hypotheses
    fork1 = analyst.fork()
    fork2 = analyst.fork()
    
    # Explore different paths in parallel
    result1, result2 = await asyncio.gather(
        fork1.run("Focus on seasonal patterns and consumer behavior."),
        fork2.run("Focus on marketing campaigns and competitive landscape.")
    )
    
    print("Fork 1 (Seasonal focus):")
    print(f"{result1['content'][:200]}...\n")
    
    print("Fork 2 (Marketing focus):")
    print(f"{result2['content'][:200]}...\n")
    
    print(f"Fork 1 messages: {len(fork1.get_messages())}")
    print(f"Fork 2 messages: {len(fork2.get_messages())}")
    print(f"Original messages: {len(analyst.get_messages())}")


# Example 3: Complex Multi-Agent System
async def example_complex_multi_agent():
    """
    Complex multi-agent system with multiple levels of coordination.
    
    Architecture:
    - Coordinator (top level)
      ├── Researcher (gathers information)
      ├── Analyst (processes data)
      └── Reporter (creates reports)
    """
    
    # Create specialized agents
    researcher = Agent(
        name="Researcher",
        system_message="You research topics and gather relevant information.",
        model="gpt-4o",
        temperature=0.2
    )
    
    analyst = Agent(
        name="Analyst",
        system_message="You analyze information and extract key insights.",
        model="gpt-4o",
        temperature=0.1
    )
    
    reporter = Agent(
        name="Reporter",
        system_message="You create clear, concise reports from analysis.",
        model="gpt-4o",
        temperature=0.3
    )
    
    # Master coordinator
    coordinator = Agent(
        name="MasterCoordinator",
        system_message="""You coordinate complex research projects.
        
        Available agents:
        - researcher: Gathers information
        - analyst: Analyzes data and extracts insights
        - reporter: Creates final reports
        
        Use them in sequence for comprehensive analysis.""",
        tools=[
            researcher.as_tool(),
            analyst.as_tool(),
            reporter.as_tool()
        ],
        model="gpt-4o"
    )
    
    # Complex task requiring multiple agents
    response = await coordinator.run("""
    Investigate the impact of AI on software development.
    
    Steps:
    1. Research current AI tools in software development
    2. Analyze their impact on productivity
    3. Create an executive summary report
    """)
    
    print("\n=== Complex Multi-Agent System ===")
    print(f"Success: {response['success']}")
    print(f"Iterations: {response['iterations']}")
    print(f"Agents called: {len(response['tool_calls'])}")
    print("\nAgent calls:")
    for i, call in enumerate(response['tool_calls'], 1):
        print(f"  {i}. {call['tool']} - {'✓' if call['success'] else '✗'}")

    print("\n=== Final Report ===")
# Example 4: Fork with Different Temperatures
async def example_creative_exploration():
    """Use forking to explore creative vs. analytical responses."""
    
    agent = Agent(
        name="Writer",
        system_message="You are a versatile writer.",
        model="gpt-4o"
    )
    
    # Initial context
    await agent.run("We're writing about artificial intelligence.")
    
    # Create forks with different configurations
    creative_fork = agent.fork()
    creative_fork.temperature = 0.9  # More creative
    creative_fork.name = "CreativeWriter"
    
    analytical_fork = agent.fork()
    analytical_fork.temperature = 0.1  # More deterministic
    analytical_fork.name = "AnalyticalWriter"
    
    # Get different perspectives
    creative, analytical = await asyncio.gather(
        creative_fork.run("Write a creative opening paragraph."),
        analytical_fork.run("Write a technical opening paragraph.")
    )
    
    print("\n=== Creative vs Analytical Exploration ===")
    print("\nCreative (temp=0.9):")
    print(creative['content'])
    
    print("\nAnalytical (temp=0.1):")
    print(analytical['content'])


async def main():
    """Run all multi-agent examples."""
    
    # Example 1: Basic multi-agent coordination
    await example_agent_as_tool()
    
    # Example 2: Conversation forking
    await example_conversation_forking()
    
    # Example 3: Complex multi-agent system
    await example_complex_multi_agent()
    
    # Example 4: Creative exploration with forking
    await example_creative_exploration()


if __name__ == "__main__":
    asyncio.run(main())
