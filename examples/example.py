"""
Agent usage examples
Demonstrates @tool decorator usage
"""
import asyncio
from toy_agent import Agent, tool
from toy_agent.tools import calculator, get_weather, search_web, read_file


# 也可以直接在示例中定义工具
@tool
def greet(name: str) -> str:
    """向用户打招呼"""
    return f"你好，{name}！很高兴认识你。"


async def main():
    # 创建Agent实例
    agent = Agent(
        name="example_agent",
        system_prompt="你是一个有用的AI助手，可以使用工具来帮助用户。",
        model="gpt-4o-mini"  # 可以根据需要修改模型
    )
    
    # 使用装饰器方式注册工具（推荐）
    # 方式1: 直接传入装饰过的函数
    agent.register_tool(calculator)
    agent.register_tool(get_weather)
    agent.register_tool(search_web)
    agent.register_tool(read_file)
    agent.register_tool(greet)
    
    # 方式2: 仍然支持传统方式（向后兼容）
    # agent.register_tool(name="calculator", description="...", func=calculator)
    
    # 运行Agent
    print("=" * 50)
    print("Agent示例")
    print("=" * 50)
    
    # 示例1: 数学计算
    print("\n示例1: 数学计算")
    result1 = await agent.run("帮我计算 123 乘以 456 等于多少？")
    print(f"Agent回复: {result1}")
    
    # 重置历史（可选）
    agent.history = [{"role": "system", "content": agent.system_prompt}]
    
    # 示例2: 天气查询
    print("\n示例2: 天气查询")
    result2 = await agent.run("北京今天天气怎么样？")
    print(f"Agent回复: {result2}")
    
    # 重置历史
    agent.history = [{"role": "system", "content": agent.system_prompt}]
    
    # 示例3: 网络搜索
    print("\n示例3: 网络搜索")
    result3 = await agent.run("搜索一下Python编程语言的相关信息")
    print(f"Agent回复: {result3}")


if __name__ == "__main__":
    asyncio.run(main())

