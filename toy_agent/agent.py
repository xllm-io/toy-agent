"""
Lightweight Agent Framework
Supports tool calling and OpenAI LLM integration
"""
import json
import asyncio
from typing import List, Dict, Any, Optional, Callable
from .tool_registry import ToolRegistry
from .llm_client import LLMClient


class Agent:
    """Lightweight Agent"""
    
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
        Initialize Agent
        
        Args:
            name: Agent name
            system_prompt: System prompt
            api_key: OpenAI API key
            base_url: API base URL
            model: Model name
            max_steps: Maximum execution steps
            timeout: Timeout in seconds
        """
        self.name = name
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.max_steps = max_steps
        self.timeout = timeout
        
        # Initialize tool registry and LLM client
        self.tool_registry = ToolRegistry()
        self.llm_client = LLMClient(api_key=api_key, base_url=base_url, model=model)
        
        # Conversation history
        self.history: List[Dict[str, str]] = []
        if self.system_prompt:
            self.history.append({
                "role": "system",
                "content": self.system_prompt
            })
    
    def register_tool(self, name: str = None, description: str = None, func: Callable = None):
        """
        Register a tool
        
        Supports two usage patterns:
        1. Traditional: register_tool(name="tool_name", description="description", func=function)
        2. Decorator: register_tool(func) or pass a function decorated with @tool
        
        Args:
            name: Tool name (optional, uses _tool_name attribute if func has it)
            description: Tool description (optional, uses _tool_description attribute if func has it)
            func: Tool function (can be sync or async, or a function decorated with @tool)
        """
        # If only func is passed (decorator usage: register_tool(function))
        if func is None and callable(name):
            func = name
            name = None
        
        # Ensure func is not None
        if func is None:
            raise ValueError("Must provide func parameter or pass a callable")
        
        # Check if function is decorated with @tool
        if hasattr(func, '_is_tool') and func._is_tool:
            tool_name = getattr(func, '_tool_name', None)
            tool_description = getattr(func, '_tool_description', None)
            
            if tool_name:
                name = name or tool_name
            if tool_description:
                description = description or tool_description
        
        # If still no name, use function name
        if not name:
            name = func.__name__
        
        # If still no description, use docstring or default
        if not description:
            description = func.__doc__ or f"{name} tool"
            if description:
                description = "\n".join(line.strip() for line in description.strip().split("\n"))
        
        self.tool_registry.register(name, description, func)
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.history.copy()
    
    def add_message(self, role: str, content: str, **kwargs):
        """
        Add message to history
        
        Args:
            role: Message role (user, assistant, system, tool)
            content: Message content
            **kwargs: Other message attributes (e.g., tool_call_id)
        """
        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.history.append(msg)
    
    async def run(self, user_input: str) -> str:
        """
        Run Agent to process user input
        
        Args:
            user_input: User input
            
        Returns:
            Agent's final response
        """
        # Add user message
        self.add_message("user", user_input)
        
        step = 0
        while step < self.max_steps:
            step += 1
            
            # Get tool list
            tools = self.tool_registry.get_tools()
            
            # Call LLM
            try:
                response = await self.llm_client.chat_async(
                    messages=self.history,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else "none"
                )
            except Exception as e:
                return f"LLM call error: {str(e)}"
            
            # Get response message
            message = response["choices"][0]["message"]
            
            # Build assistant message (include tool_calls if present)
            assistant_msg = {
                "role": message["role"],
                "content": message.get("content") or None
            }
            if message.get("tool_calls"):
                assistant_msg["tool_calls"] = message["tool_calls"]
            self.history.append(assistant_msg)
            
            # If no tool calls, return final answer
            if not message.get("tool_calls"):
                return message.get("content", "")
            
            # Execute tool calls
            for tool_call in message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                
                try:
                    # Execute tool
                    tool_result = await self.tool_registry.execute_tool(function_name, function_args)
                    
                    # Convert result to string
                    if isinstance(tool_result, (dict, list)):
                        tool_result_str = json.dumps(tool_result, ensure_ascii=False)
                    else:
                        tool_result_str = str(tool_result)
                    
                    # Add tool result to history (OpenAI format)
                    self.history.append({
                        "role": "tool",
                        "content": tool_result_str,
                        "tool_call_id": tool_call["id"]
                    })
                    
                except Exception as e:
                    # Tool execution error
                    error_msg = f"Tool {function_name} execution error: {str(e)}"
                    self.history.append({
                        "role": "tool",
                        "content": error_msg,
                        "tool_call_id": tool_call["id"]
                    })
            
            # Continue to next round of conversation
        
        return "Maximum execution steps reached"
    
    def run_sync(self, user_input: str) -> str:
        """
        Run Agent synchronously (uses async implementation internally)
        
        Args:
            user_input: User input
            
        Returns:
            Agent's final response
        """
        return asyncio.run(self.run(user_input))

