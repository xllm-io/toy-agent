"""
Demonstrates different usages of @tool decorator
"""
import asyncio
from toy_agent import Agent, tool


# 方式1: 使用装饰器，自动使用函数名和docstring
@tool
def add(a: float, b: float) -> float:
    """将两个数字相加"""
    return a + b


# 方式2: 使用装饰器，指定名称和描述
@tool(name="multiply", description="将两个数字相乘")
def multiply_numbers(a: float, b: float) -> float:
    """内部函数名是multiply_numbers，但工具名是multiply"""
    return a * b


# 方式3: 异步工具
@tool
async def fetch_data(url: str) -> str:
    """从URL获取数据（模拟）"""
    await asyncio.sleep(0.1)
    return f"从 {url} 获取的数据"


async def main():
    agent = Agent(
        name="decorator_example",
        system_prompt="你是一个数学和数据处理助手。",
        model="gpt-4o-mini"
    )
    
    # 使用装饰器方式注册工具（推荐）
    # 装饰器会自动提取工具名称和描述
    agent.register_tool(add)
    agent.register_tool(multiply_numbers)
    agent.register_tool(fetch_data)
    
    print("=" * 60)
    print("装饰器示例")
    print("=" * 60)
    
    # 测试1: 使用add工具
    print("\n测试1: 加法工具")
    result1 = await agent.run("帮我计算 15 + 27")
    print(f"Agent回复: {result1}\n")
    
    # 重置历史
    agent.history = [{"role": "system", "content": agent.system_prompt}]
    
    # 测试2: 使用multiply工具
    print("测试2: 乘法工具")
    result2 = await agent.run("帮我计算 8 乘以 9")
    print(f"Agent回复: {result2}\n")
    
    # 重置历史
    agent.history = [{"role": "system", "content": agent.system_prompt}]
    
    # 测试3: 使用fetch_data工具
    print("测试3: 数据获取工具")
    result3 = await agent.run("从 https://example.com 获取数据")
    print(f"Agent回复: {result3}\n")


if __name__ == "__main__":
    asyncio.run(main())

