"""
Tool schema generation and execution utilities.
"""
import inspect
import json
import logging
from typing import Any, Callable, Optional, get_type_hints
from .types import Tool, ToolParameter, ToolExecutionResult, AsyncToolFunction, SyncToolFunction

logger = logging.getLogger(__name__)


def generate_tool_schema(func: Callable, name: str = None, description: str = None) -> Tool:
    """
    Generate OpenAI tool schema from Python function.

    Automatically extracts function signature, type hints, and docstring
    to create OpenAI-compatible tool definition.

    Args:
        func: Python function (sync or async)
        name: Optional override for function name
        description: Optional override for function description

    Returns:
        OpenAI tool schema

    Example:
        >>> async def fetch_articles(topic: str, limit: int = 5) -> dict:
        ...     '''Fetch articles about a topic.
        ...
        ...     Args:
        ...         topic: The topic to search for (e.g., "quantum computing")
        ...         limit: Maximum number of articles to return
        ...     '''
        ...     return {"articles": []}
        >>>
        >>> schema = generate_tool_schema(fetch_articles)
        >>> schema['function']['name']
        'fetch_articles'
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    doc = inspect.getdoc(func) or ""

    # Use provided name or extract from function
    func_name = name if name else func.__name__

    # Extract function description (first line of docstring or use provided)
    if description:
        func_description = description.split('\n')[0].strip()
    else:
        func_description = doc.split('\n')[0].strip() if doc else f"Execute {func_name}"

    # Parse docstring for parameter descriptions
    param_docs = _parse_docstring_params(doc)

    # Build parameters schema
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        param_type = type_hints.get(param_name, str)
        param_schema = _python_type_to_json_schema(param_type)

        # Add description from docstring if available
        if param_name in param_docs:
            param_schema["description"] = param_docs[param_name]

        parameters["properties"][param_name] = param_schema

        # Mark as required if no default value
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(param_name)

    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": func_description,
            "parameters": parameters
        }
    }


def _parse_docstring_params(docstring: str) -> dict[str, str]:
    """
    Parse parameter descriptions from Google-style docstring.

    Args:
        docstring: Function docstring

    Returns:
        Dictionary mapping parameter names to descriptions
    """
    param_docs = {}
    lines = docstring.split('\n')

    in_args_section = False
    current_param = None

    for line in lines:
        stripped = line.strip()

        if stripped.lower() in ("args:", "arguments:", "parameters:"):
            in_args_section = True
            continue

        if in_args_section:
            # End of args section
            if stripped and not stripped.startswith(' ') and ':' not in stripped:
                break

            # New parameter line
            if ':' in stripped and not stripped.startswith(' '):
                param_name, description = stripped.split(':', 1)
                param_name = param_name.strip()
                description = description.strip()
                param_docs[param_name] = description
                current_param = param_name
            # Continuation of previous parameter description
            elif current_param and stripped:
                param_docs[current_param] += ' ' + stripped

    return param_docs


def _python_type_to_json_schema(python_type: Any) -> ToolParameter:
    """
    Convert Python type hint to JSON schema type.

    Args:
        python_type: Python type annotation

    Returns:
        JSON schema type definition
    """
    # Handle basic types
    type_map = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        dict: {"type": "object"},
        list: {"type": "array", "items": {"type": "string"}},
    }

    # Check if it's a basic type
    if python_type in type_map:
        return type_map[python_type]

    # Handle Optional types
    if hasattr(python_type, '__origin__'):
        origin = python_type.__origin__

        # Optional[X] or Union[X, None]
        if origin is type(None) or (hasattr(python_type, '__args__') and type(None) in python_type.__args__):
            # Get the non-None type
            args = [arg for arg in python_type.__args__ if arg is not type(None)]
            if args:
                schema = _python_type_to_json_schema(args[0])
                schema["nullable"] = True
                return schema

        # List[X]
        if origin is list:
            item_type = python_type.__args__[0] if python_type.__args__ else str
            return {
                "type": "array",
                "items": _python_type_to_json_schema(item_type)
            }

        # Dict[K, V]
        if origin is dict:
            return {"type": "object"}

    # Default to string
    return {"type": "string"}


async def execute_tool(
    tool_name: str,
    tool_args: dict,
    tool_map: dict[str, Callable]
) -> ToolExecutionResult:
    """
    Execute a tool function with given arguments.

    Handles both sync and async functions, with error handling.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments to pass to the tool
        tool_map: Dictionary mapping tool names to functions

    Returns:
        Tool execution result with success status and output
    """
    if tool_name not in tool_map:
        logger.error(f"Unknown tool: {tool_name}")
        return {
            "success": False,
            "result": None,
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        func = tool_map[tool_name]

        # Execute async or sync function
        if inspect.iscoroutinefunction(func):
            result = await func(**tool_args)
        else:
            result = func(**tool_args)

        return {
            "success": True,
            "result": result,
            "error": None
        }

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }


def format_tool_result(result: Any, max_length: Optional[int] = 50000) -> str:
    """
    Format tool result for inclusion in chat messages.
    Truncates large results to prevent context overflow (if max_length is set).

    Args:
        result: Tool execution result
        max_length: Maximum characters to include (None = no truncation, default: 50000)

    Returns:
        JSON string representation, truncated if necessary
    """
    if isinstance(result, (dict, list)):
        formatted = json.dumps(result, indent=2, default=str)
    elif isinstance(result, str):
        formatted = result
    else:
        formatted = str(result)

    # Truncate if max_length is set and result exceeds it
    if max_length is not None and len(formatted) > max_length:
        truncated = formatted[:max_length]
        formatted = f"{truncated}\n\n... [TRUNCATED - Original length: {len(formatted)} chars, showing first {max_length} chars]"

    return formatted
