import sys
import os
import uuid
import json
from datetime import datetime

# 设置Python搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# 导入必要的模块
from agents.base_agent import build_agent
from tools.vectorstore import build_vectorstore_from_pdf, build_vectorstore_from_document
# 导入全局向量存储缓存
from cache.vector_cache import vectorstore_cache

# 创建知识库相关目录
agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kb_dir = os.path.join(agent_dir, "knowledge_base")
kb_metadata_file = os.path.join(kb_dir, "metadata.json")
os.makedirs(kb_dir, exist_ok=True)

# 初始化知识库元数据
if not os.path.exists(kb_metadata_file):
    with open(kb_metadata_file, "w", encoding="utf-8") as f:
        json.dump({"files": []}, f, ensure_ascii=False, indent=2)

# 全局向量存储缓存（使用进程内缓存）
# vectorstore_cache = {}

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    ".txt": "text/plain",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif"
}

# 创建FastAPI应用
app = FastAPI()

# 使用绝对路径挂载静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 初始化agent
try:
    agent = build_agent()
except Exception as e:
    # 创建一个简单的回退agent以确保服务能够启动
    class SimpleAgent:
        def invoke(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
            if history and len(history) > 0:
                return f"Agent服务正在初始化中，您的查询 '{query}' 已收到，且我们检测到您有{len(history)}条历史消息。"
            return f"Agent服务正在初始化中，您的查询 '{query}' 已收到"
    agent = SimpleAgent()

class Query(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = None

@app.post("/chat")
async def chat(q: Query):
    try:
        user_message = q.query
        print(f"用户问题: {user_message}")

        # 从知识库中检索相关文档
        from agents.base_agent import retrieve_knowledge
        knowledge_content = retrieve_knowledge(user_message)
        knowledge_available = len(knowledge_content) > 0 if knowledge_content else False
        print(f"知识库检索结果长度: {len(knowledge_content) if knowledge_content else 0} 字符")

        # 检查agent是否有支持历史的invoke方法
        if hasattr(agent, 'invoke_with_history'):
            # 构建一个单一的输入字符串，包含所有信息
            if q.history and len(q.history) > 0:
                formatted_input = "历史对话:\n"
                for msg in q.history:
                    formatted_input += f"{msg['role']}: {msg['content']}\n"
                formatted_input += f"\n当前问题: {user_message}\n"
            else:
                formatted_input = user_message
            
            # 添加知识库内容和说明
            if knowledge_available:
                formatted_input += f"\n\n以下是与问题相关的知识库内容:\n{knowledge_content}\n\n请优先基于提供的知识库内容回答用户问题。如果知识库内容不足或不相关，可以结合你自己的知识进行回答，但要明确说明信息来源。"
            else:
                formatted_input += "\n\n没有找到相关的知识库内容。"
                
            response = agent.invoke_with_history(formatted_input, q.history or [])
        else:
            # 对于不支持历史的agent，将所有信息合并到单一输入字符串
            formatted_input = user_message
            
            # 添加历史信息
            if q.history and len(q.history) > 0:
                history_text = "历史对话:\n"
                for msg in q.history:
                    history_text += f"{msg['role']}: {msg['content']}\n"
                formatted_input = f"{history_text}\n当前问题: {user_message}"
            
            # 添加知识库内容和说明
            if knowledge_available:
                formatted_input += f"\n\n以下是与问题相关的知识库内容:\n{knowledge_content}\n\n请优先基于提供的知识库内容回答用户问题。如果知识库内容不足或不相关，可以结合你自己的知识进行回答，但要明确说明信息来源。"
            else:
                formatted_input += "\n\n没有找到相关的知识库内容。"
            
            # 只传递一个input键给agent.invoke
            response = agent.invoke(formatted_input)

        # 格式化响应，并添加Markdown支持
        if isinstance(response, dict) and "output" in response:
            answer = response["output"]
        else:
            answer = str(response)
        
        # 确保返回内容包含Markdown格式标记
        # 如果没有标题，添加一个默认标题
        if not (answer.startswith('#') or answer.startswith('##') or answer.startswith('###')):
            answer = "# 回答\n\n" + answer
        
        # 确保段落之间有换行
        answer = answer.replace('. ', '.\n\n').replace('? ', '?\n\n').replace('! ', '!\n\n')

        print(f"助手回答: {answer}")
        return {"response": answer}
    except Exception as e:
        print(f"处理聊天请求时出错: {str(e)}")
        return {"response": f"处理请求时出错: {str(e)}", "error": str(e)}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), history: Optional[str] = Form(None)):
    try:
        # 解析历史记录
        conversation_history = []
        if history:
            try:
                conversation_history = json.loads(history)
            except:
                pass
        
        # 确保temp目录存在
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 确保knowledge_base目录存在
        kb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
        os.makedirs(kb_dir, exist_ok=True)
        
        # 保存上传的文件到temp目录（用于临时处理）
        temp_file_path = os.path.join(temp_dir, f"temp_{os.path.basename(file.filename)}")
        content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        # 同时保存文件到knowledge_base目录并添加到知识库
        file_id = str(uuid.uuid4())
        kb_file_path = os.path.join(kb_dir, f"{file_id}_{os.path.basename(file.filename)}")
        with open(kb_file_path, "wb") as f:
            f.write(content)
        
        # 更新知识库元数据，确保文件可以被检索到
        try:
            with open(kb_metadata_file, "r+", encoding="utf-8") as f:
                metadata = json.load(f)
                
                # 检查是否已存在同名文件，防止重复上传
                existing_file = next((f for f in metadata["files"] if f["name"] == file.filename), None)
                if existing_file:
                    print(f"文件已存在于知识库中: {file.filename}，跳过重复添加")
                    # 复用已存在的file_id，避免创建新的向量存储
                    file_id = existing_file["id"]
                    kb_file_path = existing_file["path"]
                else:
                    # 获取文件类型
                    file_ext = os.path.splitext(file.filename)[1].lower()
                    # 添加新文件到元数据
                    metadata["files"].append({
                        "id": file_id,
                        "name": file.filename,
                        "path": kb_file_path,
                        "size": len(content),
                        "upload_time": datetime.now().isoformat(),
                        "type": file_ext
                    })
                    f.seek(0)
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                    f.truncate()
                    print(f"文件已添加到知识库: {file.filename}")
        except Exception as meta_err:
            print(f"更新知识库元数据失败: {str(meta_err)}")
        

        
        # 对于图片文件，使用image_captioning生成描述
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            from multimodal.image_captioning import caption_image
            try:
                image_description = caption_image(temp_file_path)
                file_content = f"这是一张图片。图片内容描述：{image_description}\n\n图片保存路径：{kb_file_path}"
                prompt = f"用户上传了一张图片，请根据图片描述回答问题。图片描述：{image_description}\n\n用户可能的问题是什么？"
            except Exception as e:
                file_content = f"图片处理失败：{str(e)}\n\n图片保存路径：{kb_file_path}"
                prompt = f"用户上传了一张图片，但处理失败：{str(e)}"
        # 对于PDF文件，使用doc_reader读取内容
        elif file_ext == '.pdf':
            from tools.doc_reader import load_pdf_content
            try:
                pdf_content = load_pdf_content(temp_file_path)
                # 取PDF前1000个字符作为摘要
                file_content = pdf_content[:1000] + "...（更多内容请查看完整文件）"
                prompt = f"请阅读以下PDF文件内容摘要，并准备回答用户可能的问题：\n{file_content}"
            except Exception as e:
                file_content = f"PDF文件处理失败：{str(e)}\n\n文件保存路径：{kb_file_path}"
                prompt = f"用户上传了一个PDF文件，但处理失败：{str(e)}"
        else:
            file_content = f"文件类型：{file_ext}\n文件大小：{len(content)}字节\n文件保存路径：{kb_file_path}"
            prompt = f"用户上传了一个{file_ext}文件，请准备回答用户可能的问题。"
        
        # 调用agent处理文件
        if hasattr(agent, 'invoke_with_history'):
            response = agent.invoke_with_history(prompt, conversation_history)
        else:
            response = agent.invoke(prompt)
        
        # 返回包含文件路径的响应，以便前端可以预览
        return {
            "response": response,
            "file_path": kb_file_path,
            "file_type": file_ext
        }
    except Exception as e:
        return {"response": f"处理上传文件时出错: {str(e)}", "error": str(e)}

# 知识库相关API端点

@app.post("/kb/upload")
async def upload_knowledge_file(file: UploadFile = File(...)):
    try:
        # 验证文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in SUPPORTED_FILE_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}{file_ext}"
        file_path = os.path.join(kb_dir, file_name)
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 更新元数据
        with open(kb_metadata_file, "r+", encoding="utf-8") as f:
            metadata = json.load(f)
            metadata["files"].append({
                "id": file_id,
                "name": file.filename,
                "path": file_path,
                "size": len(content),
                "upload_time": datetime.now().isoformat(),
                "type": file_ext
            })
            f.seek(0)
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            f.truncate()
        
        # 根据文件类型构建向量存储
        try:
            if file_ext == ".pdf":
                vectorstore = build_vectorstore_from_pdf(file_path)
                vectorstore_cache[file_id] = vectorstore
                print(f"成功构建PDF文件的向量存储")
            elif file_ext in [".jpg", ".jpeg", ".png", ".gif"]:
                # 对于图片文件，使用image_captioning生成描述
                from multimodal.image_captioning import caption_image
                from langchain.schema import Document
                from langchain.vectorstores import FAISS
                from tools.vectorstore import get_embeddings
                
                try:
                    # 生成图片描述
                    image_description = caption_image(file_path)
                    
                    # 创建文档对象
                    doc = Document(
                        page_content=f"这是一张图片。图片内容描述：{image_description}\n\n图片保存路径：{file_path}",
                        metadata={
                            "source": file_path,
                            "file_name": file.filename,
                            "file_type": file_ext
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
            elif file_ext in [".txt", ".doc", ".docx"]:
                # 对于文档文件，使用常规的文档处理
                vectorstore = build_vectorstore_from_document(file_path)
                vectorstore_cache[file_id] = vectorstore
                print(f"成功构建{file_ext}文件的向量存储")
        except Exception as e:
            print(f"构建向量存储失败: {str(e)}")
        
        return JSONResponse(content={"success": True, "file_id": file_id})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.get("/kb/files")
async def get_knowledge_files():
    try:
        with open(kb_metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # 格式化返回的文件列表
        files_list = []
        for file in metadata.get("files", []):
            files_list.append({
                "id": file["id"],
                "name": file["name"],
                "size": file["size"],
                "upload_time": file["upload_time"],
                "type": file["type"]
            })
        
        return JSONResponse(content={"success": True, "files": files_list})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@app.delete("/kb/delete/{file_id}")
async def delete_knowledge_file(file_id: str):
    try:
        with open(kb_metadata_file, "r+", encoding="utf-8") as f:
            metadata = json.load(f)
            files = metadata.get("files", [])
            
            # 查找文件
            file_to_delete = None
            for i, file in enumerate(files):
                if file["id"] == file_id:
                    file_to_delete = file
                    del files[i]
                    break
            
            if not file_to_delete:
                raise HTTPException(status_code=404, detail="文件不存在")
            
            # 删除文件
            if os.path.exists(file_to_delete["path"]):
                os.remove(file_to_delete["path"])
            
            # 从缓存中删除向量存储
            if file_id in vectorstore_cache:
                del vectorstore_cache[file_id]
            
            # 更新元数据
            f.seek(0)
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            f.truncate()
        
        return JSONResponse(content={"success": True, "message": "文件删除成功"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

# 提供首页HTML页面
@app.get("/")
async def read_root():
    # 使用绝对路径读取HTML文件
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
    

if __name__ == "__main__":
    # 直接运行时启动uvicorn服务器
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
