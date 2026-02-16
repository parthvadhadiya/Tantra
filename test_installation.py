#!/usr/bin/env python3
"""
Test script to verify Tantra works without needing API key.
Tests core functionality, imports, and structure.
"""
import asyncio
import sys


def test_imports():
    """Test that all core components can be imported."""
    print("🧪 Testing imports...")
    try:
        from tantra import Agent, LLMProvider, OpenAIProvider
        from tantra import extract_json_from_response, extract_html_from_response
        from tantra import generate_tool_schema, execute_tool
        from tantra import AgentConfig, AgentResponse, Tool, ToolExecutionResult, Message
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_tool_schema_generation():
    """Test that tool schemas are generated correctly."""
    print("\n🧪 Testing tool schema generation...")
    try:
        from tantra import generate_tool_schema
        
        async def test_tool(city: str, limit: int = 5) -> dict:
            """
            Test tool for weather.
            
            Args:
                city: City name
                limit: Max results
                
            Returns:
                Weather data
            """
            return {"city": city, "temp": 72}
        
        schema = generate_tool_schema(test_tool)
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "test_tool"
        assert "city" in schema["function"]["parameters"]["properties"]
        assert "city" in schema["function"]["parameters"]["required"]
        assert "limit" not in schema["function"]["parameters"]["required"]
        
        print("   ✅ Tool schema generation works")
        return True
    except Exception as e:
        print(f"   ❌ Tool schema generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_creation():
    """Test that agents can be created."""
    print("\n🧪 Testing agent creation...")
    try:
        from tantra import Agent
        
        # Test basic agent creation
        agent = Agent(
            name="TestAgent",
            system_message="You are a test agent.",
            model="gpt-4o"
        )
        
        assert agent.name == "TestAgent"
        assert agent.model == "gpt-4o"
        assert agent.messages == []
        assert agent.total_usage["total_tokens"] == 0
        
        print("   ✅ Agent creation works")
        return True
    except Exception as e:
        print(f"   ❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_with_tools():
    """Test agent with tools."""
    print("\n🧪 Testing agent with tools...")
    try:
        from tantra import Agent
        
        def simple_tool(text: str) -> dict:
            """Simple test tool."""
            return {"result": f"Processed: {text}"}
        
        agent = Agent(
            name="ToolAgent",
            system_message="You are a helpful assistant.",
            tools=[simple_tool],
            model="gpt-4o"
        )
        
        assert len(agent.tool_schemas) == 1
        assert "simple_tool" in agent.tool_map
        assert agent.tool_schemas[0]["function"]["name"] == "simple_tool"
        
        print("   ✅ Agent with tools works")
        return True
    except Exception as e:
        print(f"   ❌ Agent with tools failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_forking():
    """Test conversation forking."""
    print("\n🧪 Testing conversation forking...")
    try:
        from tantra import Agent
        
        agent = Agent(
            name="Original",
            system_message="Test agent",
            model="gpt-4o"
        )
        
        # Add some messages
        agent.messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "Hello"}
        ]
        
        # Fork the agent
        forked = agent.fork()
        
        assert forked.name == "Original_fork"
        assert len(forked.messages) == 2
        assert forked.messages[0]["content"] == "System message"
        
        # Modify fork shouldn't affect original
        forked.messages.append({"role": "assistant", "content": "Hi"})
        assert len(forked.messages) == 3
        assert len(agent.messages) == 2
        
        print("   ✅ Conversation forking works")
        return True
    except Exception as e:
        print(f"   ❌ Conversation forking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_as_tool():
    """Test agent-as-tool pattern."""
    print("\n🧪 Testing agent-as-tool pattern...")
    try:
        from tantra import Agent
        
        sub_agent = Agent(
            name="SubAgent",
            system_message="You are a specialized agent.",
            model="gpt-4o"
        )
        
        # Convert to tool
        tool_func = sub_agent.as_tool()
        
        assert callable(tool_func)
        assert tool_func.__name__ == "subagent"
        assert "SubAgent" in tool_func.__doc__
        
        print("   ✅ Agent-as-tool pattern works")
        return True
    except Exception as e:
        print(f"   ❌ Agent-as-tool failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test utility functions."""
    print("\n🧪 Testing utility functions...")
    try:
        from tantra import extract_json_from_response, extract_html_from_response
        
        # Test JSON extraction
        json_text = '{"name": "test", "value": 42}'
        result = extract_json_from_response(json_text)
        assert result == {"name": "test", "value": 42}
        
        # Test JSON in markdown
        markdown_json = '```json\n{"key": "value"}\n```'
        result = extract_json_from_response(markdown_json)
        assert result == {"key": "value"}
        
        print("   ✅ Utility functions work")
        return True
    except Exception as e:
        print(f"   ❌ Utility functions failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_interface():
    """Test provider interface."""
    print("\n🧪 Testing provider interface...")
    try:
        from tantra import LLMProvider, OpenAIProvider
        from abc import ABC
        
        # Check LLMProvider is abstract
        assert issubclass(LLMProvider, ABC)
        
        # Check OpenAIProvider exists
        provider = OpenAIProvider(api_key="test-key")
        assert provider is not None
        
        print("   ✅ Provider interface works")
        return True
    except Exception as e:
        print(f"   ❌ Provider interface failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Testing Tantra Installation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_tool_schema_generation,
        test_agent_creation,
        test_agent_with_tools,
        test_conversation_forking,
        test_agent_as_tool,
        test_utils,
        test_provider_interface,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Tantra is working correctly.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
