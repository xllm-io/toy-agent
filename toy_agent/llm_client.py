"""
OpenAI LLM client wrapper
Supports synchronous and asynchronous calls
"""
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from openai import AsyncOpenAI


class LLMClient:
    """OpenAI LLM client"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM client
        
        Args:
            api_key: OpenAI API key, reads from OPENAI_API_KEY env var if not provided
            base_url: API base URL, for compatibility with other OpenAI-compatible APIs
            model: Model name, defaults to gpt-4o-mini
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Must provide api_key or set OPENAI_API_KEY environment variable")
        
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        
        # Initialize sync and async clients
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, tool_choice: str = "auto", extra_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call LLM synchronously
        
        Args:
            messages: Message list, format: [{"role": "user", "content": "..."}]
            tools: Tool list in OpenAI API format
            tool_choice: Tool selection strategy, "auto", "none", or specific tool
            
        Returns:
            API response
        """
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        
        if extra_body:
            kwargs["extra_body"] = extra_body

        response = self.client.chat.completions.create(**kwargs)
        print("[LLMClient] response: ", response)
        
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
    
    async def chat_async(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, tool_choice: str = "auto", extra_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call LLM asynchronously
        
        Args:
            messages: Message list
            tools: Tool list
            tool_choice: Tool selection strategy
            
        Returns:
            API response
        """
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        
        if extra_body:
            kwargs["extra_body"] = extra_body


        try:
            response = await self.async_client.chat.completions.create(**kwargs)
        except Exception as e:
            print("[LLMClient] async error: ", e)
            return {
                "id": "",
                "choices": [],
                "usage": {}
            }

        # print("[LLMClient] async response.choices: ", response.choices[0].message.reasoning_details or None)
        
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
                    ],
                    "reasoning_details": response.choices[0].message.reasoning_details or None
                }
            }],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
        }

