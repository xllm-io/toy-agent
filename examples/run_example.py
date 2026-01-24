"""
Simple test script
For verifying basic functionality of the Agent framework
Demonstrates @tool decorator usage
"""
import asyncio
from operator import mul
import os
from toy_agent import Agent, tool
from toy_agent.tools import search_web, get_weather, read_file, multi_edit


async def test_agent():
    """测试天气工具"""
    print("=" * 60)
    print("测试3: 天气查询工具（使用@tool装饰器）")
    print("=" * 60)
    
    agent = Agent(
        name="gemini_3_pro_agent",
        system_prompt="你是一个助手，可以查询城市天气，也可以在网络上搜索信息。你可以同时使用多个工具，完成用户的需求。",
        model=None or os.getenv("MODEL", "gpt-4o-mini")
    )
    
    # 使用装饰器方式注册工具
    agent.register_tool(get_weather)
    agent.register_tool(search_web)  # 同时注册greet工具
    
    try:
        result = await agent.run("帮我查询一下北京天气，并给我提供下北京最新的新闻信息。")
        print(f"Agent回复: {result}\n")
    except Exception as e:
        print(f"错误: {e}\n")

async def test_file_agent():
    """测试文件工具"""
    print("=" * 60)
    print("测试: 文件工具（使用@tool装饰器）")
    print("=" * 60)
    
    agent = Agent(
        name="file_agent",
        system_prompt="你是一个助手，可以读取或者创建文件。",
        model=None or os.getenv("MODEL", "gpt-4o-mini")
    )
    
    # 使用装饰器方式注册工具
    agent.register_tool(read_file)
    agent.register_tool(multi_edit)

    try:
        result = await agent.run("帮我写一个React Native代码开发TODO。保存路径为/Users/ewalker/Downloads/mydev/agent/toy-agent/data/code/input.txt")
        print(f"Agent回复: {result}\n")
    except Exception as e:
        print(f"错误: {e}\n")

async def main():
    """运行所有测试"""
    print("\n开始测试轻量级Agent框架\n")
    
    
    # await test_agent()
    await test_file_agent()

if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "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"
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
    os.environ["MODEL"] = "alibaba/tongyi-deepresearch-30b-a3b:free"
    asyncio.run(main())

