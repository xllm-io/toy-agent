"""
简单测试脚本
用于验证Agent框架的基本功能
展示@tool装饰器的用法
"""
import asyncio
import os
from agent import Agent
from tools import calculator, get_weather
from tool_registry import tool


# 定义一个测试工具
@tool
def greet(name: str) -> str:
    """向用户打招呼"""
    return f"你好，{name}！"


async def test_basic():
    """测试基本功能"""
    print("=" * 60)
    print("测试1: 基本对话（无工具）")
    print("=" * 60)
    
    agent = Agent(
        name="test_agent",
        system_prompt="你是一个友好的AI助手。",
        model="claude37-sonnet"
    )
    
    try:
        result = await agent.run("你好，请介绍一下你自己")
        print(f"Agent回复: {result}\n")
    except Exception as e:
        print(f"错误: {e}\n")


async def test_calculator():
    """测试计算器工具"""
    print("=" * 60)
    print("测试2: 计算器工具（使用@tool装饰器）")
    print("=" * 60)
    
    agent = Agent(
        name="calculator_agent",
        system_prompt="你是一个数学助手，可以使用计算器工具。",
        model="claude37-sonnet"
    )
    
    # 使用装饰器方式注册工具
    agent.register_tool(calculator)
    
    try:
        result = await agent.run("帮我计算 25 乘以 4 等于多少？")
        print(f"Agent回复: {result}\n")
    except Exception as e:
        print(f"错误: {e}\n")


async def test_weather():
    """测试天气工具"""
    print("=" * 60)
    print("测试3: 天气查询工具（使用@tool装饰器）")
    print("=" * 60)
    
    agent = Agent(
        name="weather_agent",
        system_prompt="你是一个天气助手，可以查询城市天气。",
        model="claude37-sonnet"
    )
    
    # 使用装饰器方式注册工具
    agent.register_tool(get_weather)
    agent.register_tool(greet)  # 同时注册greet工具
    
    try:
        result = await agent.run("北京今天天气怎么样？")
        print(f"Agent回复: {result}\n")
    except Exception as e:
        print(f"错误: {e}\n")


async def main():
    """运行所有测试"""
    print("\n开始测试轻量级Agent框架\n")
    
    # 注意：需要设置OPENAI_API_KEY环境变量
    # export OPENAI_API_KEY="your-api-key"
    
    await test_basic()
    await test_calculator()
    await test_weather()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

