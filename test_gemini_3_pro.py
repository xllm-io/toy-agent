"""
Simple test script
For verifying basic functionality of the Agent framework
Demonstrates @tool decorator usage
"""
import asyncio
import os
from toy_agent import Agent, tool
from tools import search_web, get_weather


async def test_gemini_3_pro():
    """测试天气工具"""
    print("=" * 60)
    print("测试3: 天气查询工具（使用@tool装饰器）")
    print("=" * 60)
    
    agent = Agent(
        name="gemini_3_pro_agent",
        system_prompt="你是一个助手，可以查询城市天气，也可以在网络上搜索信息。你可以同时使用多个工具，完成用户的需求。",
        model="gemini-3-pro-preview"
    )
    
    # 使用装饰器方式注册工具
    agent.register_tool(get_weather)
    agent.register_tool(search_web)  # 同时注册greet工具
    
    try:
        result = await agent.run("帮我查询一下北京天气，并给我提供下北京最新的新闻信息。")
        print(f"Agent回复: {result}\n")
    except Exception as e:
        print(f"错误: {e}\n")


async def main():
    """运行所有测试"""
    print("\n开始测试轻量级Agent框架\n")
    
    
    await test_gemini_3_pro()

if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["OPENAI_BASE_URL"] = ""
    asyncio.run(main())

