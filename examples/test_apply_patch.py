"""
测试 apply_patch 工具
"""
import os
import sys
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toy_agent.tools.apply_patch import apply_patch


def test_apply_patch():
    """测试 apply_patch 工具"""
    print("=" * 60)
    print("测试 apply_patch 工具")
    print("=" * 60)
    
    # 创建临时目录和文件用于测试
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.py")
    
    with open(test_file, 'w') as f:
        f.write("""def hello():
    print("Hello")
    print("World")
    return True
""")
    
    print(f"创建测试文件: {test_file}")
    
    # 创建一个简单的补丁，使用相对路径
    patch = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 def hello():
     print("Hello")
-    print("World")
+    print("Universe")
     return True
 """
    
    print("\n应用补丁...")
    result = apply_patch(patch, base_path=temp_dir)
    print(f"结果:\n{result}\n")
    
    # 读取修改后的文件
    with open(test_file, 'r') as f:
        content = f.read()
        print("修改后的文件内容:")
        print(content)
        print("\n预期内容应包含 'Universe' 而不是 'World'")
    
    # 清理
    os.unlink(test_file)
    os.rmdir(temp_dir)
    print(f"\n已删除测试文件: {test_file}")


if __name__ == "__main__":
    test_apply_patch()

