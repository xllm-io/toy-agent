"""
天气工具
"""
from typing import Dict, Any
from toy_agent import tool


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

