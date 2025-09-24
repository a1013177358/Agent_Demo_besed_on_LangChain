# -*- coding: utf-8 -*-
"""
@File    : base_agent.py
@Time    : 2025/9/25 15:13
@Desc    : 基于gemini-2.5-flash模型的智能体实现，包含工具调用能力
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载.env文件中的环境变量
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# 导入必要的模块
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from memory.memory import memory
from tools.search_tool import search_web
from tools.doc_reader import load_pdf_content
from tools.vectorstore import build_vectorstore_from_pdf, build_vectorstore_from_document, get_embeddings
from multimodal.image_captioning import caption_image

# 配置常量
SIMILARITY_THRESHOLD = 1.5  # 相似度阈值，可根据实际情况调整

# 构建文档向量检索器 - 使用项目中实际存在的PDF文件路径
agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(agent_dir, "../docs/GB+38031-2025.pdf")
vectorstore = build_vectorstore_from_pdf(pdf_path)
retriever = vectorstore.as_retriever()

# 知识库路径
kb_dir = os.path.join(agent_dir, "knowledge_base")
kb_metadata_file = os.path.join(kb_dir, "metadata.json")

# 从app.main导入全局向量存储缓存
# from app.main import vectorstore_cache
# 从缓存模块导入全局向量存储缓存
from cache.vector_cache import vectorstore_cache

# 从知识库中检索相关文档
def retrieve_knowledge(query: str, k: int = 3) -> str:
    """
    从知识库中检索与查询相关的文档
    
    参数 query: 查询文本
    参数 k: 返回的相关文档数量
    返回值: 检索到的文档内容，用换行符分隔，包含文档来源信息
    """
    try:
        # 加载知识库元数据
        if not os.path.exists(kb_metadata_file):
            return ""
        
        with open(kb_metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        all_relevant_docs = []
        
        # 遍历所有支持的文档文件进行检索
        supported_file_types = [".pdf", ".txt", ".docx", ".jpg", ".jpeg", ".png", ".gif"]
        for file in metadata.get("files", []):
            file_type = file["type"]
            if file_type not in supported_file_types:
                continue
                
            file_id = file["id"]
            file_path = file["path"]
            file_name = file["name"]
            
            # 获取或创建向量存储 - 确保只构建一次
            if file_id not in vectorstore_cache:
                try:
                    # 根据文件类型选择合适的向量存储构建方法
                    print(f"为文件 {file_name} 构建向量存储...")
                    if file_type == ".pdf":
                        vectorstore_cache[file_id] = build_vectorstore_from_pdf(file_path)
                    elif file_type in [".jpg", ".jpeg", ".png", ".gif"]:
                        # 对于图片文件，使用image_captioning生成描述并构建向量存储
                        from multimodal.image_captioning import caption_image
                        from langchain.schema import Document
                        from langchain.vectorstores import FAISS
                        from langchain.embeddings import HuggingFaceEmbeddings
                        
                        try:
                            # 生成图片描述
                            image_description = caption_image(file_path)
                            
                            # 创建文档对象
                            doc = Document(
                                page_content=f"这是一张图片。图片内容描述：{image_description}\n\n图片保存路径：{file_path}",
                                metadata={
                                    "source": file_path,
                                    "file_name": file_name,
                                    "file_type": file_type
                                }
                            )
                            
                            # 获取嵌入模型（使用缓存）
                            embeddings = get_embeddings()
                            
                            # 构建向量存储
                            vectorstore = FAISS.from_documents([doc], embeddings)
                            vectorstore_cache[file_id] = vectorstore
                            print(f"成功构建图片文件的向量存储")
                        except Exception as image_err:
                            print(f"处理图片文件失败: {str(image_err)}")
                            continue
                    else:
                        vectorstore_cache[file_id] = build_vectorstore_from_document(file_path)
                    print(f"文件 {file_name} 向量存储已缓存，后续查询将直接使用缓存")
                except Exception as e:
                    print(f"构建向量存储失败 ({file_name}): {str(e)}")
                    continue
            else:
                # 记录缓存使用情况，以便调试
                print(f"使用缓存的向量存储处理文件: {file_name}")
                
            # 执行相似度检索
            vs = vectorstore_cache[file_id]
            results = vs.similarity_search_with_score(query, k=k)
            
            # 将结果添加到相关文档列表
            for doc, score in results:
                # 只添加相似度足够高的文档
                if score < SIMILARITY_THRESHOLD:
                    # 添加文档来源信息，方便用户了解信息出处
                    source_info = f"【来自文件: {file_name}】\n"
                    all_relevant_docs.append((source_info + doc.page_content, score))
        
        # 按相似度排序并取前k个结果
        all_relevant_docs.sort(key=lambda x: x[1])
        top_docs = [doc for doc, _ in all_relevant_docs[:k]]
        
        # 合并文档内容，如果没有找到相关文档，返回提示信息
        if top_docs:
            return "\n\n".join(top_docs)
        else:
            return "知识库中未找到与查询相关的内容。"
    except Exception as e:
        print(f"检索知识库失败: {str(e)}")
        return "知识库检索过程中发生错误。"


def retrieve_doc(query: str) -> str:
    """
    从向量存储中检索相关文档
    """
    try:
        docs = retriever.get_relevant_documents(query)
        result = "\n\n".join([doc.page_content for doc in docs])
        return result
    except Exception as e:
        print(f"检索文档失败: {str(e)}")
        return "无法检索文档内容，请稍后再试"

import time

def build_agent():
    """
    构建智能体，添加重试机制确保初始化成功
    
    返回: 初始化完成的智能体实例
    """
    max_retries = 3
    retry_delay = 2  # 秒
    
    for attempt in range(max_retries):
        try:
            # 定义工具
            tools = [
                Tool(
                    name="PDF Semantic Search",
                    func=retrieve_doc,
                    description="当用户需要关于预设PDF文档的详细信息时使用此工具。输入应该是一个详细的问题。",
                ),
                Tool(
                    name="Web Search",
                    func=search_web,
                    description="当用户需要最新的、实时的信息或文档中没有的信息时使用此工具。输入应该是一个搜索查询。",
                ),
            ]

            # 初始化LLM模型
            llm = ChatOpenAI(
                model='gemini-2.5-flash',
                openai_api_key=os.getenv('GOOGLE_API_KEY'),
                openai_api_base='https://generativelanguage.googleapis.com/v1beta/openai/',
                temperature=0,
            )

            # 定义系统提示
            prompt = PromptTemplate(
                template="""你是一个专业的智能助手。请根据以下说明和信息回答用户的问题。

你拥有两个工具可以使用：
1. PDF Semantic Search: 用于获取预设PDF文档中的详细信息
2. Web Search: 用于获取最新的、实时的信息或文档中没有的信息

请严格遵循以下规则：
- 首先**必须**检查系统提供的知识库内容是否与问题相关，如果相关，请**结合知识库内容**回答。
- 知识库可能包含PDF、TXT和DOCX等不同格式文档的内容，请根据问题和内容相关性进行综合分析
- 如果知识库内容明确提到"无相关知识库内容"，并且问题与预设PDF文档内容相关，请使用PDF Semantic Search获取信息
- 如果问题需要最新的、实时的信息或不在任何文档中，请使用Web Search获取信息
- 如果没有相关信息，直接基于你的知识回答，不要编造信息
- 回答要简洁明了，使用自然语言，避免使用过于技术性的术语

用户的问题是：{input}

系统提供的知识库内容：
{knowledge_base}
""",
                input_variables=["input", "knowledge_base"],
            )

            # 创建Agent
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                memory=memory,
                handle_parsing_errors=True,
            )

            print(f"智能体初始化成功 (尝试 {attempt + 1}/{max_retries})")
            return agent
        except Exception as e:
            print(f"智能体初始化失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"{retry_delay}秒后重试...")
                time.sleep(retry_delay)
            else:
                print("所有重试均失败，创建回退Agent")
                # 创建一个简单的回退agent以确保服务能够启动
                class SimpleAgent:
                    def invoke(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
                        if isinstance(query, dict) and "input" in query:
                            user_query = query["input"]
                        else:
                            user_query = str(query)
                        
                        if history and len(history) > 0:
                            return f"Agent服务正在初始化中，您的查询 '{user_query}' 已收到，且我们检测到您有{len(history)}条历史消息。"
                        return f"Agent服务正在初始化中，您的查询 '{user_query}' 已收到"
                    
                    def invoke_with_history(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
                        return self.invoke(query, history)
                
                return SimpleAgent()


if __name__ == '__main__':
    print("正在初始化AI智能体...")
    try:
        ai_agent = build_agent()
        print("智能体初始化成功！")
        # rsp = ai_agent.invoke({"input": "北京今天天气怎么样？"})
        # print(rsp)
    except Exception as e:
        print(f"运行出错: {str(e)}")
        import traceback
        traceback.print_exc()