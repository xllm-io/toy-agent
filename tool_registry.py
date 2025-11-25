"""
轻量级工具注册系统
支持工具注册、查询和执行
"""
import json
import inspect
from typing import Dict, Callable, Any, List, Optional
from dataclasses import dataclass
from functools import wraps


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable


def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    工具装饰器
    
    用法:
        @tool(name="my_tool", description="工具描述")
        def my_tool(param: str) -> str:
            return f"结果: {param}"
    
    或者使用函数名和docstring:
        @tool
        def my_tool(param: str) -> str:
            '''工具描述'''
            return f"结果: {param}"
    
    Args:
        name: 工具名称，如果不提供则使用函数名
        description: 工具描述，如果不提供则使用函数的docstring
    """
    def decorator(func: Callable) -> Callable:
        # 确定工具名称
        tool_name = name or func.__name__
        
        # 确定工具描述
        tool_description = description or func.__doc__ or f"{tool_name}工具"
        # 清理docstring（去除多余空白）
        if tool_description:
            tool_description = "\n".join(line.strip() for line in tool_description.strip().split("\n"))
        
        # 在函数上添加工具元数据
        func._tool_name = tool_name
        func._tool_description = tool_description
        func._is_tool = True
        
        return func
    
    # 如果直接作为装饰器使用（没有括号），func就是第一个参数
    if callable(name):
        func = name
        tool_name = func.__name__
        tool_description = func.__doc__ or f"{tool_name}工具"
        if tool_description:
            tool_description = "\n".join(line.strip() for line in tool_description.strip().split("\n"))
        func._tool_name = tool_name
        func._tool_description = tool_description
        func._is_tool = True
        return func
    
    return decorator


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, name: str, description: str, func: Callable):
        """
        注册工具
        
        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数
        """
        # 从函数签名提取参数信息
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
                "type": "string"  # 默认类型为string
            }
            
            # 尝试从类型注解获取类型
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
            
            # 从默认值判断是否必需
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
        获取所有工具的OpenAI格式描述
        
        Returns:
            工具列表，格式符合OpenAI API要求
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
        执行工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if name not in self._tools:
            raise ValueError(f"工具 {name} 未注册")
        
        tool = self._tools[name]
        
        # 检查函数是否为异步函数
        if inspect.iscoroutinefunction(tool.func):
            return await tool.func(**arguments)
        else:
            return tool.func(**arguments)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具对象"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有已注册的工具名称"""
        return list(self._tools.keys())

