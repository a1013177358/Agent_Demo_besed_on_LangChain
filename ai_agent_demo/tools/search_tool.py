# -*- coding: utf-8 -*-
"""
@File    : search_tool.py
@Time    : 2025/9/25 15:13
@Desc    : 基于Tavily搜索的网络搜索工具
"""
import os
import warnings

# 禁用LangSmith警告
warnings.filterwarnings("ignore", category=Warning, module="langsmith")

# 设置环境变量禁用LangSmith跟踪
os.environ['LANGCHAIN_TRACING_V2'] = 'false'

from dotenv import load_dotenv

# 加载.env文件中的环境变量
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# 使用新的Tavily搜索方法
from langchain_tavily import TavilySearch

def search_web(query: str) -> str:
    try:
        # 初始化Tavily搜索
        search = TavilySearch(
            api_key=os.getenv('TAVILY_API_KEY'),
            k=5,  # 返回5个搜索结果
            search_depth="basic",  # 基础搜索
            include_raw_content=False  # 不包含原始内容
        )
        
        # 执行搜索
        results = search.invoke(query)
        
        # 检查结果类型并适当处理
        if isinstance(results, str):
            # 如果结果是字符串，直接返回
            return results
        elif hasattr(results, 'get'):
            # 如果结果是一个字典，提取content字段
            return results.get('content', str(results))
        elif isinstance(results, list):
            # 如果结果是一个列表，格式化每个元素
            formatted_results = []
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    formatted_result = {
                        "title": result.get("title", f"结果 {i+1}"),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0)
                    }
                    formatted_results.append(formatted_result)
                else:
                    # 对于非字典元素，转为字符串
                    formatted_results.append(str(result))
            
            return str(formatted_results)
        else:
            # 对于其他类型，转为字符串
            return str(results)
    except Exception as e:
        print(f"搜索出错: {str(e)}")
        return f"搜索失败: {str(e)}"

if __name__ == '__main__':
    # 测试搜索功能
    print("正在测试搜索功能...")
    rsp = search_web("今天是哪天？")
    print(rsp)
