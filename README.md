# Lightweight Agent Framework

A lightweight Agent framework that supports tool registration and invocation, OpenAI LLM model calls, and other core features.

## Features

- ✅ **Tool Registration & Invocation**: Support for both synchronous and asynchronous tool registration and execution
- ✅ **OpenAI LLM Integration**: Wrapped OpenAI API with tool calling support
- ✅ **Conversation History Management**: Automatic conversation history management
- ✅ **Multi-step Reasoning**: Support for multi-round tool calls and reasoning
- ✅ **Simple & Easy to Use**: Clean API design, easy to extend

## Installation

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd toy-agent

# Install using pip
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Install as a package

```bash
pip install .
```

## Configuration

Set up OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="your-base-url-here"  # option, default: https://api.openai.com/v1
```

Or pass it when creating the agent:

```python
agent = Agent(api_key="your-api-key")
```

## Quick Start

### Basic Usage

```python
from toy_agent import Agent, tool
from toy_agent.tools import calculator, get_weather

# Create Agent
agent = Agent(
    name="my_agent",
    system_prompt="You are a helpful AI assistant.",
    model="gpt-4o-mini"
)

# Register tools
agent.register_tool(calculator)
agent.register_tool(get_weather)

# Run Agent
result = await agent.run("Calculate 10 + 20 for me")
print(result)
```

### Defining Tools

#### Method 1: Using @tool Decorator (Recommended)

```python
from toy_agent import tool

# Synchronous tool
@tool(name="my_tool", description="Tool description")
def my_tool(param1: str, param2: int) -> str:
    return f"Result: {param1}, {param2}"

# Or use function name and docstring
@tool
def my_async_tool(query: str) -> dict:
    """Async tool description"""
    await asyncio.sleep(0.1)
    return {"result": query}

# Register tools (decorator automatically extracts name and description)
agent.register_tool(my_tool)
agent.register_tool(my_async_tool)
```

#### Method 2: Traditional Method (Backward Compatible)

```python
# Synchronous tool
def my_tool(param1: str, param2: int) -> str:
    """Tool description"""
    return f"Result: {param1}, {param2}"

# Async tool
async def my_async_tool(query: str) -> dict:
    """Async tool description"""
    await asyncio.sleep(0.1)
    return {"result": query}

# Register tools
agent.register_tool(name="my_tool", description="Tool description", func=my_tool)
agent.register_tool(name="my_async_tool", description="Async tool description", func=my_async_tool)
```

## Built-in Tools

The framework provides several built-in tools in `toy_agent.tools`:

| Tool | Module | Description |
|------|--------|-------------|
| `calculator` | `calculator.py` | Basic math operations (add, subtract, multiply, divide) |
| `get_weather` | `weather.py` | Get weather information for a city (simulated) |
| `search_web` | `search.py` | Web search (async, simulated) |
| `read_file` | `file_ops.py` | Read file contents |
| `multi_edit` | `file_ops.py` | Atomic multi-edit operations on a single file |

### Using Built-in Tools

```python
from toy_agent.tools import calculator, get_weather, search_web, read_file, multi_edit

# Or import individual modules
from toy_agent.tools.calculator import calculator
from toy_agent.tools.file_ops import multi_edit, read_file
```

### multi_edit Tool

The `multi_edit` tool allows multiple atomic edits to a single file:

```python
result = multi_edit(
    file_path="/path/to/file.py",
    edits=[
        {"old_string": "old_text_1", "new_string": "new_text_1"},
        {"old_string": "old_text_2", "new_string": "new_text_2", "replace_all": True}
    ]
)
```

## Project Structure

```
toy-agent/
├── toy_agent/                # Core package
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # Agent core class
│   ├── tool_registry.py      # Tool registration system
│   ├── llm_client.py         # OpenAI LLM client wrapper
│   └── tools/                # Built-in tools
│       ├── __init__.py       # Tools export
│       ├── calculator.py     # Calculator tool
│       ├── weather.py        # Weather tool
│       ├── search.py         # Web search tool
│       └── file_ops.py       # File operations (read_file, multi_edit)
├── examples/                 # Example scripts
│   ├── example.py            # Basic usage examples
│   ├── example_decorator.py  # Decorator usage examples
│   ├── run_example.py        # Run example
│   ├── test_simple.py        # Simple test script
│   └── test_gemini_3_pro.py  # Gemini model test
├── data/                     # Test data
├── requirements.txt          # Dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## API Documentation

### Agent Class

#### Initialization

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

#### Methods

- `register_tool(name=None, description=None, func=None)`: Register a tool
  - Decorator method: `register_tool(func)` - Pass a function decorated with `@tool`
  - Traditional method: `register_tool(name="tool_name", description="description", func=function)`
- `run(user_input: str) -> str`: Run Agent asynchronously
- `run_sync(user_input: str) -> str`: Run Agent synchronously
- `get_history() -> List[Dict[str, str]]`: Get conversation history
- `add_message(role: str, content: str, **kwargs)`: Add message to history

### ToolRegistry Class

- `register(name: str, description: str, func: Callable)`: Register a tool
- `get_tools() -> List[Dict[str, Any]]`: Get all tools in OpenAI format
- `execute_tool(name: str, arguments: Dict[str, Any]) -> Any`: Execute a tool
- `list_tools() -> List[str]`: List all registered tool names

### @tool Decorator

- `@tool(name=None, description=None)`: Tool decorator
  - With parameters: `@tool(name="tool_name", description="description")`
  - Without parameters: `@tool` - Automatically uses function name and docstring

### LLMClient Class

- `chat(messages, tools=None, tool_choice="auto")`: Call LLM synchronously
- `chat_async(messages, tools=None, tool_choice="auto")`: Call LLM asynchronously

## Examples

Run example code:

```bash
cd examples
python example.py
python run_example.py
```

## Notes

1. Make sure to set up the correct OpenAI API key
2. Type annotations on tool function parameters help automatically generate tool descriptions
3. Tools can be synchronous or asynchronous functions, the framework handles both automatically
4. The `max_steps` parameter controls the maximum execution steps for the Agent to prevent infinite loops

## Extension

The framework is designed to be simple and easy to extend:

1. **Add New Tools**: Create new tool files in `toy_agent/tools/`, then export them in `__init__.py`
2. **Custom LLM Client**: Replace `llm_client.py` to support other LLM services
3. **Enhance Agent Features**: Inherit the `Agent` class to add custom functionality

## License

MIT License
