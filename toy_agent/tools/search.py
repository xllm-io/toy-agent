"""
网络搜索工具
"""
import asyncio
from typing import Dict, Any
from toy_agent import tool


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

