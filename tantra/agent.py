from typing import Any, Dict, Optional, AsyncGenerator, Union
import inspect
import asyncio
from abc import ABC

from .llm import LLMFactory, LLMConfig
from .memory import Memory
from .tools import ToolRegistry
from .session import Session
from .config import AgentConfig
from .utils.logger import logger

class Agent(ABC):
    def __init__(self, config: Union[AgentConfig, Dict[str, Any]]):
        if isinstance(config, dict):
            self.config = AgentConfig.from_dict(config)
        else:
            self.config = config
            
        # Initialize LLM
        llm_config = LLMConfig(
            provider=self.config.llm_type,
            model=self.config.llm_model,
            api_key=self.config.llm_api_key,
            **self.config.llm_options
        )
        self.llm = LLMFactory.create(llm_config)
        
        # Initialize other components
        self.session: Optional[Session] = None
        self.memory = Memory.load(self.config.memory_path) if self.config.memory_path else Memory()
        self.tools = ToolRegistry()
        
        # Add basic facts to memory
        self.memory.add_fact("agent_name", self.config.name)
        self.memory.add_fact("agent_instructions", self.config.instructions)
        
    @property
    def name(self) -> str:
        return self.config.name
        
    @property
    def instructions(self) -> str:
        return self.config.instructions
        
    async def on_enter(self) -> Optional[str]:
        """Called when agent starts a new session.
        Return a string to send an initial message, or None for no message."""
        return f"Hello! I am {self.name}. How can I help you today?"
    
    async def on_exit(self) -> Optional[str]:
        """Called when agent ends a session.
        Return a string to send a farewell message, or None for no message."""
        return "Thank you for your time. Have a great day!"
        
    async def on_error(self, error: Exception) -> Optional[str]:
        """Called when an error occurs.
        Return a string to send an error message, or None for no message."""
        return "I apologize, but I encountered an error. Please try again."
        
    async def on_timeout(self) -> Optional[str]:
        """Called when a response times out.
        Return a string to send a timeout message, or None for no message."""
        return "I apologize, but I took too long to respond. Please try again."
        
    async def on_invalid_input(self, input_str: str) -> Optional[str]:
        """Called when input validation fails.
        Return a string to send an error message, or None for no message."""
        return "I'm sorry, but I couldn't understand that input. Could you try again?"
    
    def register_tool(self, func):
        """Register a new tool"""
        self.tools.register(func)
        
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        tool_func = self.tools.get_tool(tool_name)
        if not tool_func:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await tool_func(**kwargs)
    
    async def think(self, message: str) -> str:
        """Process a message and return a response"""
        # Add message to memory only if it's not a duplicate
        last_message = self.memory.messages[-1] if self.memory.messages else None
        if not last_message or last_message['content'] != message:
            self.memory.add_message("user", message)
        
        # Build prompt
        logger.debug("Building prompt with:")
        context = self.memory.get_context()
        logger.debug(f"Context: {context}")
        
        tools = self.tools.get_tool_descriptions()
        logger.debug(f"Available tools: {tools}")
        
        logger.debug(f"User message: {message}")
        
        # Get current tool and parameters if any
        current_tool = self.memory.get_fact("current_tool")
        current_params = {}
        if current_tool:
            current_params = self.memory.get_collected_params(current_tool)
            logger.debug(f"Current tool: {current_tool} with params: {current_params}")
        
        param_state = f'Currently collecting parameters for: {current_tool}\nCollected so far: {current_params}' if current_tool else 'No active parameter collection'
        
        prompt = f"""You are an AI assistant that uses tools to help users. Follow these rules:

1. When you have ACTUAL values for ALL required parameters:
   - Use the tool immediately with collected values
   - Example: @set_reminder(task='buy groceries', time='tomorrow at 2pm')

2. When you DON'T have all required values:
   - Ask for ONLY ONE missing parameter at a time
   - Ask in a natural way: "What task would you like to be reminded about?"
   - Never ask for parameters you already have
   - Never use placeholder values like 'task' or 'time'

3. Parameter Collection State:
   {param_state}

Available Tools:
{tools}

Previous Context:
{context}

User: {message}

Assistant (ask for ONE missing parameter OR use @tool with collected values):"""
        
        logger.debug(f"Generated prompt:\n{prompt}")
        
        # Get response from LLM
        response = await self.llm.chat(prompt)
        logger.debug(f"LLM response: {response}")
        
        return response

    
    async def stream_response(self, response: str) -> AsyncGenerator[str, None]:
        """Stream response to user"""
        if not self.config.streaming:
            yield response
            return
            
        self.memory.add_message("assistant", response)
        words = response.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3])
            yield chunk
            await asyncio.sleep(0.1)
            
    async def say(self, message: str) -> None:
        """Send a direct message without generation"""
        if not self.session:
            raise RuntimeError("No active session")
            
        self.memory.add_message("assistant", message)
        if self.config.streaming:
            async for chunk in self.stream_response(message):
                await self.session.say(chunk)
        else:
            await self.session.say(message)
    
    async def generate(self, prompt: str) -> str:
        """Generate a response using the agent's LLM"""
        self.memory.add_message("user", prompt)
        response = await self.think(prompt)
        
        if response.startswith("@"):
            try:
                # Parse tool call
                tool_call = response[1:].split("(")
                tool_name = tool_call[0]
                args_str = tool_call[1].rstrip(')')
                logger.debug(f"Parsed tool call: {tool_name}({args_str})")
                
                # Get tool
                if tool_name not in self.tools._tools:
                    raise ValueError(f"Unknown tool: {tool_name}")
                tool = self.tools._tools[tool_name]
                
                # Parse provided args
                args = {}
                if args_str:
                    # TODO: Use safer parsing in production
                    args = eval(f"dict({args_str})")
                logger.debug(f"Parsed args: {args}")
                
                # Get any previously collected parameters
                collected = self.memory.get_collected_params(tool_name)
                args.update(collected)  # Add collected params to current args
                logger.debug(f"Combined with collected params: {args}")
                
                # Analyze required parameters
                required_params = []
                param_info = {}
                for name, param in tool.signature.parameters.items():
                    if name == 'self':
                        continue
                    
                    # Get parameter metadata
                    param_type = param.annotation.__name__ if param.annotation != inspect._empty else 'Any'
                    has_default = param.default != inspect._empty
                    default_value = param.default if has_default else None
                    
                    param_info[name] = {
                        'type': param_type,
                        'required': not has_default,
                        'default': default_value
                    }
                    
                    if not has_default:
                        required_params.append(name)
                
                logger.debug(f"Required parameters: {required_params}")
                logger.debug(f"Parameter info: {param_info}")
                
                # Check for missing required params
                missing_params = [p for p in required_params if p not in args]
                if missing_params:
                    logger.debug(f"Missing parameters: {missing_params}")
                    
                    # Save any new parameters
                    for param, value in args.items():
                        if param not in collected:
                            logger.debug(f"Adding new parameter: {param}={value}")
                            self.memory.add_param(tool_name, param, value)
                    
                    # Get docstring and param descriptions
                    docstring = tool.description
                    missing_info = []
                    for param in missing_params:
                        info = param_info[param]
                        type_str = info['type']
                        missing_info.append(f"{param} ({type_str})")
                    
                    # Ask for missing params
                    prompt = f"""I need more information to use the {tool_name} tool.
                    Missing required parameters: {', '.join(missing_info)}
                    
                    Tool description: {docstring}
                    Already collected: {', '.join(f'{k}={v}' for k, v in collected.items())}
                    
                    Please ask the user for the {missing_params[0]} parameter in a natural way.
                    Do not ask for any other parameters.
                    """
                    logger.debug(f"Asking for missing params with prompt:\n{prompt}")
                    return await self.think(prompt)
                
                # All required params present, execute tool
                logger.debug(f"Executing {tool_name} with args: {args}")
                result = await self.execute_tool(tool_name, **args)
                logger.debug(f"Tool returned: {result}")
                
                # Clear collected params after successful execution
                logger.debug(f"Clearing collected params for {tool_name}")
                self.memory.clear_collected_params(tool_name)
                
                # Generate natural response
                prompt = f"""Tool {tool_name} returned: {result}
                Tool description: {tool.description}
                
                Please provide a natural response incorporating this information.
                """
                logger.debug(f"Generating natural response with prompt:\n{prompt}")
                return await self.think(prompt)
                
            except Exception as e:
                logger.error(f"Error in generate: {str(e)}", exc_info=True)
                return await self.on_error(e)
            
        return response
            
    async def on_event(self, event: Dict[str, Any]) -> Optional[str]:
        """Handle incoming events"""
        try:
            if event["type"] == "USER_MESSAGE":
                return await self.generate(event["content"])
                
            elif event["type"] == "SESSION_START":
                message = await self.on_enter()
                if message:
                    await self.say(message)
                    
            elif event["type"] == "SESSION_END":
                message = await self.on_exit()
                if message:
                    await self.say(message)
                    
            elif event["type"] == "TIMEOUT":
                message = await self.on_timeout()
                if message:
                    await self.say(message)
                    
            elif event["type"] == "INVALID_INPUT":
                message = await self.on_invalid_input(event.get("content", ""))
                if message:
                    await self.say(message)
                    
        except Exception as e:
            message = await self.on_error(e)
            if message:
                await self.say(message)
            raise
    
    def attach_session(self, session: Session):
        """Attach a session to this agent"""
        self.session = session
