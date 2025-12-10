import inspect
from typing import Callable, Dict, Any, List

class ToolRegistry:
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register_tool(cls, name: str = None):
        """Decorator to register a function as a tool."""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            cls._registry[tool_name] = func
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        """Retrieve a tool by name."""
        return cls._registry.get(name)

    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tools."""
        return list(cls._registry.keys())

    @classmethod
    def execute_tool(cls, name: str, *args, **kwargs) -> Any:
        """Execute a tool by name."""
        func = cls.get_tool(name)
        if not func:
            raise ValueError(f"Tool '{name}' not found.")
        
        # Simple argument handling - could be expanded
        return func(*args, **kwargs)
