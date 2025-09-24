# -*- coding: utf-8 -*-
"""
@File    : vectorstore.py
@Time    : 2025/9/25 16:23
@Desc    : 文档向量存储构建与相似度检索模块，支持PDF/TXT/DOCX格式
"""
import os
import time
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

# 全局缓存，用于存储预加载的嵌入模型
_embeddings_cache = {}

# 默认配置参数
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def get_embeddings(model_name=DEFAULT_EMBEDDING_MODEL):
    """
    获取嵌入模型，优先从缓存中获取，不存在则创建新实例
    
    参数 model_name: 嵌入模型名称
    返回值: HuggingFaceEmbeddings实例
    """
    if model_name not in _embeddings_cache:
        start_time = time.time()
        print(f"加载嵌入模型: {model_name}")
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        _embeddings_cache[model_name] = embeddings
        print(f"嵌入模型加载完成，耗时: {time.time() - start_time:.2f}秒")
    return _embeddings_cache[model_name]

def build_vectorstore_from_document(file_path=None, chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP):
    """
    从文档文件构建向量存储，支持PDF/TXT/DOCX格式
    
    参数 file_path: 文档文件路径
    参数 chunk_size: 文本分块大小
    参数 chunk_overlap: 分块重叠大小
    返回值: FAISS向量存储对象
    """
    # 获取当前脚本所在目录的父目录（即ai_agent_demo目录）
    agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 如果未提供file_path，则使用默认路径
    if file_path is None:
        file_path = os.path.join(agent_dir, "temp_全球AI生态全景概览.pdf")
    
    file_path = Path(file_path)
    file_ext = file_path.suffix.lower()
    
    print(f"加载文档文件: {file_path}")
    
    # 根据文件扩展名选择合适的加载器
    if file_ext == '.pdf':
        loader = PyPDFLoader(str(file_path))
    elif file_ext == '.txt':
        loader = TextLoader(str(file_path), encoding='utf-8')
    elif file_ext == '.docx':
        loader = Docx2txtLoader(str(file_path))
    else:
        raise ValueError(f"不支持的文件格式: {file_ext}")
    
    # 加载文档
    docs = loader.load()
    
    # 文本分片处理
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # 每个分片的字符数
        chunk_overlap=chunk_overlap,  # 分片间重叠的字符数
        separators=["\n\n", "\n", ". ", ", ", " "]
    )
    split_docs = text_splitter.split_documents(docs)
    
    print(f"文档加载完成，共 {len(split_docs)} 个分片")
    
    # 获取嵌入模型（使用缓存）
    embeddings = get_embeddings()
    
    # 构建向量存储
    vectorstore = FAISS.from_documents(split_docs, embedding=embeddings)
    return vectorstore

# 保留原函数名以保持兼容性
def build_vectorstore_from_pdf(pdf_path=None):
    """
    从PDF文件构建向量存储（兼容旧接口）
    
    参数 pdf_path: PDF文件路径，如果为None则使用默认路径
    返回值: FAISS向量存储对象
    """
    return build_vectorstore_from_document(pdf_path)


def test_similarity_search(query_text, k=3):
    """
    测试相似度检索功能，输入查询文本，返回top k相似的内容
    
    参数 query_text: 查询文本
    参数 k: 返回的相似文档数量，默认为3
    返回值: 包含相似文档和检索时间的结果字典
    """
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 构建向量存储
        vectorstore = build_vectorstore_from_pdf()
        
        # 执行相似度检索
        search_start_time = time.time()
        results = vectorstore.similarity_search_with_score(query_text, k=k)
        search_end_time = time.time()
        
        # 计算总耗时和检索耗时
        total_time = time.time() - start_time
        search_time = search_end_time - search_start_time
        
        # 格式化结果
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": score
            })
        
        # 返回结果和性能指标
        return {
            "query": query_text,
            "results": formatted_results,
            "performance": {
                "total_time_seconds": total_time,
                "search_time_seconds": search_time,
                "results_count": len(formatted_results)
            },
            "success": True
        }
    except Exception as e:
        print(f"相似度检索出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "query": query_text,
            "error": str(e),
            "success": False
        }


def print_search_results(results):
    """
    打印检索结果的格式化输出
    
    参数 results: test_similarity_search函数返回的结果字典
    """
    if not results["success"]:
        print(f"\n检索失败: {results['error']}")
        return
    
    print(f"\n=== 查询文本: '{results['query']}' ===")
    print(f"总耗时: {results['performance']['total_time_seconds']:.4f} 秒")
    print(f"检索耗时: {results['performance']['search_time_seconds']:.4f} 秒")
    print(f"返回结果数: {results['performance']['results_count']}\n")
    
    for i, result in enumerate(results['results'], 1):
        print(f"--- 结果 #{i} (相似度得分: {result['similarity_score']:.4f}) ---")
        # 截断显示内容，最多显示200个字符
        content_preview = result['content'][:200] + ("..." if len(result['content']) > 200 else "")
        print(f"内容预览: {content_preview}")
        print(f"来源: 第 {result['metadata'].get('page', '未知')} 页")
        print()


if __name__ == "__main__":
    """主函数，用于测试相似度检索功能"""
    print("=== PDF文档相似度检索测试 ===")
    
    # 示例查询文本，用户可以根据需要修改
    sample_query = "人工智能生态系统的发展趋势"
    print(f"\n使用示例查询: '{sample_query}'")
    
    # 执行相似度检索测试
    results = test_similarity_search(sample_query, k=3)
    
    # 打印格式化的检索结果
    print_search_results(results)
    
    # 允许用户输入自定义查询
    try:
        custom_query = input("\n请输入您的查询文本 (直接按回车退出): ")
        if custom_query.strip():
            print(f"\n执行自定义查询: '{custom_query}'")
            custom_results = test_similarity_search(custom_query, k=3)
            print_search_results(custom_results)
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n用户输入处理出错: {str(e)}")
    
    print("\n=== 测试完成 ===")
