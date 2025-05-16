import inspect
from typing import Any, Callable, Dict, List, Optional

class Tool:
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or "No description available"
        self.signature = inspect.signature(func)
        
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def get_description(self) -> str:
        params = []
        for name, param in self.signature.parameters.items():
            if name == 'self':
                continue
            annotation = param.annotation if param.annotation != inspect._empty else Any
            default = f"={param.default}" if param.default != inspect._empty else ""
            params.append(f"{name}: {annotation.__name__}{default}")
            
        return f"{self.name}({', '.join(params)})\n    {self.description}"

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        
    def register(self, func: Optional[Callable] = None, *, name: Optional[str] = None, description: Optional[str] = None) -> Callable:
        if func is None:
            return lambda f: self.register(f, name=name, description=description)
            
        tool_obj = Tool(func, name, description)
        self._tools[tool_obj.name] = tool_obj
        return func
        
    def get_tool(self, name: str) -> Optional[Callable]:
        tool = self._tools.get(name)
        return tool.func if tool else None
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all registered tools"""
        if not self._tools:
            return "No tools available."
            
        descriptions = ["Available tools:"]
        for tool in self._tools.values():
            descriptions.append(tool.get_description())
        return "\n".join(descriptions)
    
    def list_tools(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self._tools.keys())

def tool(name: Optional[str] = None, description: Optional[str] = None) -> Callable:
    """Decorator to register a function as a tool"""
    def decorator(func: Callable) -> Callable:
        registry = ToolRegistry()
        return registry.register(func, name=name, description=description)
    return decorator
