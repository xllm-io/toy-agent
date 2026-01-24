"""
apply_patch 工具使用示例
演示如何在 Agent 中使用 apply_patch 工具
"""
import asyncio
import os
from toy_agent import Agent
from toy_agent.tools import apply_patch, read_file


async def main():
    """演示 apply_patch 工具的使用"""
    print("=" * 60)
    print("apply_patch 工具使用示例")
    print("=" * 60)
    
    agent = Agent(
        name="patch_agent",
        system_prompt="你是一个代码助手，可以使用 apply_patch 工具来应用补丁修改文件。",
        model=os.getenv("MODEL", "gpt-4o-mini")
    )
    
    # 注册工具
    agent.register_tool(apply_patch)
    agent.register_tool(read_file)
    
    # 示例：应用一个简单的补丁
    patch_example = """--- a/example.py
+++ b/example.py
@@ -1,3 +1,3 @@
 def greet(name):
-    return f"Hello, {name}!"
+    return f"你好, {name}!"
 
 print(greet("World"))
"""
    
    print("\n示例补丁内容:")
    print(patch_example)
    
    try:
        # 让 agent 应用补丁
        result = await agent.run(
            f"请应用以下补丁到文件 /tmp/example.py:\n\n{patch_example}"
        )
        print(f"\nAgent 回复:\n{result}\n")
    except Exception as e:
        print(f"错误: {e}\n")


if __name__ == "__main__":
    os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
    asyncio.run(main())

