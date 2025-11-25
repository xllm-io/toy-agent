"""
轻量级Agent框架
支持工具调用和OpenAI LLM集成
"""
import json
import asyncio
from typing import List, Dict, Any, Optional, Callable
from tool_registry import ToolRegistry
from llm_client import LLMClient


class Agent:
    """轻量级Agent"""
    
    def __init__(
        self,
        name: str = "agent",
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_steps: int = 10,
        timeout: float = 300.0
    ):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            system_prompt: 系统提示词
            api_key: OpenAI API密钥
            base_url: API基础URL
            model: 模型名称
            max_steps: 最大执行步数
            timeout: 超时时间（秒）
        """
        self.name = name
        self.system_prompt = system_prompt or "你是一个有用的AI助手。"
        self.max_steps = max_steps
        self.timeout = timeout
        
        # 初始化工具注册表和LLM客户端
        self.tool_registry = ToolRegistry()
        self.llm_client = LLMClient(api_key=api_key, base_url=base_url, model=model)
        
        # 对话历史
        self.history: List[Dict[str, str]] = []
        if self.system_prompt:
            self.history.append({
                "role": "system",
                "content": self.system_prompt
            })
    
    def register_tool(self, name: str = None, description: str = None, func: Callable = None):
        """
        注册工具
        
        支持两种用法：
        1. 传统方式：register_tool(name="tool_name", description="描述", func=function)
        2. 装饰器方式：register_tool(func) 或直接传入使用@tool装饰的函数
        
        Args:
            name: 工具名称（可选，如果func有_tool_name属性则使用该属性）
            description: 工具描述（可选，如果func有_tool_description属性则使用该属性）
            func: 工具函数（可以是同步或异步函数，或使用@tool装饰的函数）
        """
        # 如果只传入了func（装饰器用法：register_tool(function)）
        if func is None and callable(name):
            func = name
            name = None
        
        # 确保func不为None
        if func is None:
            raise ValueError("必须提供func参数或传入可调用对象")
        
        # 检查是否是使用@tool装饰的函数
        if hasattr(func, '_is_tool') and func._is_tool:
            tool_name = getattr(func, '_tool_name', None)
            tool_description = getattr(func, '_tool_description', None)
            
            if tool_name:
                name = name or tool_name
            if tool_description:
                description = description or tool_description
        
        # 如果仍然没有名称，使用函数名
        if not name:
            name = func.__name__
        
        # 如果仍然没有描述，使用docstring或默认值
        if not description:
            description = func.__doc__ or f"{name}工具"
            if description:
                description = "\n".join(line.strip() for line in description.strip().split("\n"))
        
        self.tool_registry.register(name, description, func)
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.history.copy()
    
    def add_message(self, role: str, content: str, **kwargs):
        """
        添加消息到历史
        
        Args:
            role: 消息角色 (user, assistant, system, tool)
            content: 消息内容
            **kwargs: 其他消息属性（如tool_call_id等）
        """
        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.history.append(msg)
    
    async def run(self, user_input: str) -> str:
        """
        运行Agent，处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent的最终回复
        """
        # 添加用户消息
        self.add_message("user", user_input)
        
        step = 0
        while step < self.max_steps:
            step += 1
            
            # 获取工具列表
            tools = self.tool_registry.get_tools()
            
            # 调用LLM
            try:
                response = await self.llm_client.chat_async(
                    messages=self.history,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else "none"
                )
            except Exception as e:
                return f"LLM调用错误: {str(e)}"
            
            # 获取响应消息
            message = response["choices"][0]["message"]
            
            # 构建assistant消息（包含tool_calls如果存在）
            assistant_msg = {
                "role": message["role"],
                "content": message.get("content") or None
            }
            if message.get("tool_calls"):
                assistant_msg["tool_calls"] = message["tool_calls"]
            self.history.append(assistant_msg)
            
            # 如果没有工具调用，返回最终答案
            if not message.get("tool_calls"):
                return message.get("content", "")
            
            # 执行工具调用
            for tool_call in message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                
                try:
                    # 执行工具
                    tool_result = await self.tool_registry.execute_tool(function_name, function_args)
                    
                    # 将结果转换为字符串
                    if isinstance(tool_result, (dict, list)):
                        tool_result_str = json.dumps(tool_result, ensure_ascii=False)
                    else:
                        tool_result_str = str(tool_result)
                    
                    # 添加工具结果到历史（OpenAI格式）
                    self.history.append({
                        "role": "tool",
                        "content": tool_result_str,
                        "tool_call_id": tool_call["id"]
                    })
                    
                except Exception as e:
                    # 工具执行错误
                    error_msg = f"工具 {function_name} 执行错误: {str(e)}"
                    self.history.append({
                        "role": "tool",
                        "content": error_msg,
                        "tool_call_id": tool_call["id"]
                    })
            
            # 继续下一轮对话
        
        return "达到最大执行步数限制"
    
    def run_sync(self, user_input: str) -> str:
        """
        同步运行Agent（内部使用异步实现）
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent的最终回复
        """
        return asyncio.run(self.run(user_input))

