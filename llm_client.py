"""
OpenAI LLM客户端封装
支持同步和异步调用
"""
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from openai import AsyncOpenAI


class LLMClient:
    """OpenAI LLM客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        初始化LLM客户端
        
        Args:
            api_key: OpenAI API密钥，如果不提供则从环境变量OPENAI_API_KEY读取
            base_url: API基础URL，用于兼容其他OpenAI兼容的API
            model: 模型名称，默认为gpt-4o-mini
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供api_key或设置环境变量OPENAI_API_KEY")
        
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        
        # 初始化同步和异步客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, tool_choice: str = "auto") -> Dict[str, Any]:
        """
        同步调用LLM
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}]
            tools: 工具列表，格式符合OpenAI API要求
            tool_choice: 工具选择策略，"auto"、"none"或具体工具
            
        Returns:
            API响应
        """
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        
        response = self.client.chat.completions.create(**kwargs)
        
        return {
            "id": response.id,
            "choices": [{
                "message": {
                    "role": response.choices[0].message.role,
                    "content": response.choices[0].message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in (response.choices[0].message.tool_calls or [])
                    ]
                }
            }],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
        }
    
    async def chat_async(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, tool_choice: str = "auto") -> Dict[str, Any]:
        """
        异步调用LLM
        
        Args:
            messages: 消息列表
            tools: 工具列表
            tool_choice: 工具选择策略
            
        Returns:
            API响应
        """
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        
        response = await self.async_client.chat.completions.create(**kwargs)
        print(f"zhangjun response: {response.model_dump()}")
        
        return {
            "id": response.id,
            "choices": [{
                "message": {
                    "role": response.choices[0].message.role,
                    "content": response.choices[0].message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in (response.choices[0].message.tool_calls or [])
                    ]
                }
            }],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
        }

