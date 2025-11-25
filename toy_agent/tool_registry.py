"""
Lightweight tool registration system
Supports tool registration, querying, and execution
"""
import json
import inspect
from typing import Dict, Callable, Any, List, Optional
from dataclasses import dataclass
from functools import wraps


@dataclass
class Tool:
    """Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable


def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    Tool decorator
    
    Usage:
        @tool(name="my_tool", description="Tool description")
        def my_tool(param: str) -> str:
            return f"Result: {param}"
    
    Or use function name and docstring:
        @tool
        def my_tool(param: str) -> str:
            '''Tool description'''
            return f"Result: {param}"
    
    Args:
        name: Tool name, uses function name if not provided
        description: Tool description, uses function docstring if not provided
    """
    def decorator(func: Callable) -> Callable:
        # Determine tool name
        tool_name = name or func.__name__
        
        # Determine tool description
        tool_description = description or func.__doc__ or f"{tool_name} tool"
        # Clean docstring (remove extra whitespace)
        if tool_description:
            tool_description = "\n".join(line.strip() for line in tool_description.strip().split("\n"))
        
        # Add tool metadata to function
        func._tool_name = tool_name
        func._tool_description = tool_description
        func._is_tool = True
        
        return func
    
    # If used directly as decorator (without parentheses), func is the first argument
    if callable(name):
        func = name
        tool_name = func.__name__
        tool_description = func.__doc__ or f"{tool_name} tool"
        if tool_description:
            tool_description = "\n".join(line.strip() for line in tool_description.strip().split("\n"))
        func._tool_name = tool_name
        func._tool_description = tool_description
        func._is_tool = True
        return func
    
    return decorator


class ToolRegistry:
    """Tool registry"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, name: str, description: str, func: Callable):
        """
        Register a tool
        
        Args:
            name: Tool name
            description: Tool description
            func: Tool function
        """
        # Extract parameter information from function signature
        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_info = {
                "type": "string"  # Default type is string
            }
            
            # Try to get type from type annotation
            if param.annotation != inspect.Parameter.empty:
                type_name = str(param.annotation)
                if 'int' in type_name:
                    param_info["type"] = "integer"
                elif 'float' in type_name:
                    param_info["type"] = "number"
                elif 'bool' in type_name:
                    param_info["type"] = "boolean"
                elif 'list' in type_name or 'List' in type_name:
                    param_info["type"] = "array"
            
            # Determine if required from default value
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
            
            parameters["properties"][param_name] = param_info
        
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            func=func
        )
        
        self._tools[name] = tool
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools in OpenAI format
        
        Returns:
            Tool list in OpenAI API format
        """
        tools = []
        for tool in self._tools.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return tools
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if name not in self._tools:
            raise ValueError(f"Tool {name} is not registered")
        
        tool = self._tools[name]
        
        # Check if function is async
        if inspect.iscoroutinefunction(tool.func):
            return await tool.func(**arguments)
        else:
            return tool.func(**arguments)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool object"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())

