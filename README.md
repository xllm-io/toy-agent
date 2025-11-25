# 轻量级Agent框架

一个轻量级的Agent框架，支持工具注册与调用、OpenAI LLM模型调用等核心功能。

## 功能特性

- ✅ **工具注册与调用**: 支持同步和异步工具注册和执行
- ✅ **OpenAI LLM集成**: 封装OpenAI API，支持工具调用
- ✅ **对话历史管理**: 自动管理对话历史
- ✅ **多步推理**: 支持Agent多轮工具调用和推理
- ✅ **简单易用**: 简洁的API设计，易于扩展

## 安装

```bash
pip install -r requirements.txt
```

## 配置

设置OpenAI API密钥：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

或者在使用时传入：

```python
agent = Agent(api_key="your-api-key")
```

## 快速开始

### 基本使用

```python
from agent import Agent
from tool_registry import tool
from tools import calculator

# 创建Agent
agent = Agent(
    name="my_agent",
    system_prompt="你是一个有用的AI助手。",
    model="gpt-4o-mini"
)

# 使用装饰器方式注册工具（推荐）
agent.register_tool(calculator)

# 运行Agent
result = await agent.run("帮我计算 10 + 20")
print(result)
```

### 定义工具

#### 方式1: 使用 @tool 装饰器（推荐）

```python
from tool_registry import tool

# 同步工具
@tool(name="my_tool", description="工具描述")
def my_tool(param1: str, param2: int) -> str:
    return f"处理结果: {param1}, {param2}"

# 或者使用函数名和docstring
@tool
def my_async_tool(query: str) -> dict:
    """异步工具描述"""
    await asyncio.sleep(0.1)
    return {"result": query}

# 注册工具（装饰器会自动提取名称和描述）
agent.register_tool(my_tool)
agent.register_tool(my_async_tool)
```

#### 方式2: 传统方式（向后兼容）

```python
# 同步工具
def my_tool(param1: str, param2: int) -> str:
    """工具描述"""
    return f"处理结果: {param1}, {param2}"

# 异步工具
async def my_async_tool(query: str) -> dict:
    """异步工具描述"""
    await asyncio.sleep(0.1)
    return {"result": query}

# 注册工具
agent.register_tool(name="my_tool", description="工具描述", func=my_tool)
agent.register_tool(name="my_async_tool", description="异步工具描述", func=my_async_tool)
```

## 项目结构

```
toy-agent/
├── agent.py              # Agent核心类
├── tool_registry.py      # 工具注册系统
├── llm_client.py         # OpenAI LLM客户端封装
├── tools.py              # 示例工具集合
├── example.py            # 使用示例
├── requirements.txt      # 依赖包
└── README.md             # 项目文档
```

## API文档

### Agent类

#### 初始化

```python
Agent(
    name: str = "agent",
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = "gpt-4o-mini",
    max_steps: int = 10,
    timeout: float = 300.0
)
```

#### 方法

- `register_tool(name=None, description=None, func=None)`: 注册工具
  - 装饰器方式：`register_tool(func)` - 传入使用`@tool`装饰的函数
  - 传统方式：`register_tool(name="tool_name", description="描述", func=function)`
- `run(user_input: str) -> str`: 异步运行Agent
- `run_sync(user_input: str) -> str`: 同步运行Agent
- `get_history() -> List[Dict[str, str]]`: 获取对话历史
- `add_message(role: str, content: str, **kwargs)`: 添加消息到历史

### ToolRegistry类

- `register(name: str, description: str, func: Callable)`: 注册工具
- `get_tools() -> List[Dict[str, Any]]`: 获取所有工具的OpenAI格式描述
- `execute_tool(name: str, arguments: Dict[str, Any]) -> Any`: 执行工具
- `list_tools() -> List[str]`: 列出所有已注册的工具名称

### @tool 装饰器

- `@tool(name=None, description=None)`: 工具装饰器
  - 如果提供参数：`@tool(name="tool_name", description="描述")`
  - 如果不提供参数：`@tool` - 自动使用函数名和docstring

### LLMClient类

- `chat(messages, tools=None, tool_choice="auto")`: 同步调用LLM
- `chat_async(messages, tools=None, tool_choice="auto")`: 异步调用LLM

## 示例

运行示例代码：

```bash
python example.py
```

## 注意事项

1. 确保设置了正确的OpenAI API密钥
2. 工具函数的参数类型注解有助于自动生成工具描述
3. 工具可以是同步或异步函数，框架会自动处理
4. `max_steps`参数控制Agent的最大执行步数，防止无限循环

## 扩展

框架设计简洁，易于扩展：

1. **添加新工具**: 在`tools.py`中定义新工具，然后注册到Agent
2. **自定义LLM客户端**: 可以替换`llm_client.py`以支持其他LLM服务
3. **增强Agent功能**: 可以继承`Agent`类添加自定义功能

## 许可证

MIT License

