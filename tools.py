"""
示例工具集合
展示如何定义和使用工具
"""
import json
import asyncio
from typing import Dict, Any
from tool_registry import tool


# 同步工具示例
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


@tool(name="get_weather", description="获取指定城市的天气信息")
def get_weather(city: str) -> Dict[str, Any]:
    """
    获取天气信息（模拟）
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字典
    """
    # 这是一个模拟的天气工具
    weather_data = {
        "北京": {"temperature": 20, "condition": "晴天", "humidity": 60},
        "上海": {"temperature": 22, "condition": "多云", "humidity": 70},
        "广州": {"temperature": 25, "condition": "小雨", "humidity": 80},
    }
    
    return weather_data.get(city, {
        "temperature": 20,
        "condition": "未知",
        "humidity": 50,
        "note": f"未找到{city}的天气信息，返回默认值"
    })


# 异步工具示例
@tool(name="search_web", description="在网络上搜索信息")
async def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    网络搜索工具（模拟）
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数
        
    Returns:
        搜索结果
    """
    # 模拟网络延迟
    await asyncio.sleep(0.1)
    
    # 这是一个模拟的搜索结果
    return {
        "query": query,
        "results": [
            {
                "title": f"关于 {query} 的结果 {i+1}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"这是关于 {query} 的搜索结果摘要 {i+1}"
            }
            for i in range(min(max_results, 3))
        ]
    }


@tool(name="read_file", description="读取文件内容")
async def read_file(file_path: str) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"错误: 文件 {file_path} 不存在"
    except Exception as e:
        return f"错误: 读取文件时发生异常 - {str(e)}"

