"""
计算器工具
"""
from toy_agent import tool


@tool(name="calculator", description="执行基本数学运算（加法、减法、乘法、除法）")
def calculator(operation: str, a: float, b: float) -> float:
    """
    计算器工具
    
    Args:
        operation: 操作类型 (add, subtract, multiply, divide)
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        计算结果
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else float('inf')
    }
    
    if operation not in operations:
        raise ValueError(f"不支持的操作: {operation}")
    
    return operations[operation](a, b)

