# AI Agent Demo

一个基于大语言模型的智能体演示项目，具备知识库检索、网络搜索和多模态理解能力，支持命令行和Web界面交互。

## ✨ 功能特性

- **智能对话**：基于Google Gemini-2.5-Flash模型的自然语言交互能力
- **知识库检索**：支持PDF/TXT/DOCX格式文档的向量化存储和语义检索
- **网络搜索**：集成Tavily搜索API，获取最新网络信息
- **多模态理解**：支持图像内容分析与描述生成
- **会话记忆**：记住对话历史，提供连贯的交流体验
- **双界面支持**：提供命令行和Web界面两种交互方式

## 🚀 快速开始

### 环境要求

- Python 3.9+ 
- 安装依赖：`pip install -r requirements.txt`

### 配置API密钥

1. 将`.env.example`复制为`.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑`.env`文件，填入您的API密钥：
   ```env
   # Google API密钥（必需）
   GOOGLE_API_KEY='your_google_api_key_here'
   
   # Tavily API密钥（用于网络搜索功能）
   TAVILY_API_KEY='your_tavily_api_key_here'
   ```

### 启动方式

#### 命令行模式

```bash
python main.py
```

#### Web服务器模式

```bash
python app/main.py
```

启动后，访问 http://127.0.0.1:8000 即可使用Web界面。

## 📚 使用指南

### 命令行交互

启动命令行模式后，直接输入您的问题，智能体将根据知识库和网络信息进行回答。

### Web界面交互

1. 在浏览器中打开 http://127.0.0.1:8000
2. 在输入框中输入问题，点击发送按钮
3. 查看智能体的回复结果

### 添加知识库文件

1. 将文档（PDF/TXT/DOCX格式）放入`knowledge_base`目录
2. 更新`knowledge_base/metadata.json`文件，添加新文件的元数据信息
3. 重启服务，新文档将被加载到向量存储中

## 🛠 技术栈

- **核心框架**：LangChain、FastAPI
- **Web服务器**：Uvicorn
- **AI模型**：
  - Gemini-2.5-Flash (主要语言模型)
  - BAAI/bge-small-zh-v1.5 (嵌入模型)
  - Salesforce/blip-image-captioning-base (图像描述模型)
- **向量存储**：FAISS
- **文档处理**：PyPDF、python-docx
- **网络搜索**：Tavily API

## 📁 项目结构

```
ai_agent_demo/
├── main.py              # 命令行模式入口
├── agents/              # 智能体实现
│   └── base_agent.py    # 基础智能体实现
├── app/                 # Web应用部分
│   └── main.py          # Web服务器入口
├── tools/               # 工具函数
│   ├── vectorstore.py   # 向量存储构建与检索
│   └── search_tool.py   # 网络搜索工具
├── memory/              # 会话记忆管理
│   └── memory.py        # 对话历史存储
├── multimodal/          # 多模态处理
│   └── image_captioning.py  # 图像描述生成
├── knowledge_base/      # 知识库文件
│   ├── metadata.json    # 知识库元数据
│   └── [文档文件]        # PDF/TXT/DOCX格式文档
├── requirements.txt     # 项目依赖
└── .env.example         # 环境变量示例文件
```

## ⚙️ 配置说明

### 环境变量

- `GOOGLE_API_KEY`：Google Gemini API密钥（必需）
- `TAVILY_API_KEY`：Tavily搜索API密钥（可选，用于网络搜索功能）
- `LANGCHAIN_TRACING_V2`：LangSmith跟踪开关（可选，默认关闭）
- `LANGCHAIN_API_KEY`：LangSmith API密钥（可选）

### 知识库元数据格式

`knowledge_base/metadata.json`文件包含知识库文档的元数据信息，格式如下：

```json
[
  {
    "filename": "example.pdf",
    "path": "knowledge_base\\example.pdf",
    "type": "pdf",
    "description": "示例文档"
  }
]
```

## 🔧 开发指南

### 安装开发依赖

```bash
pip install -r requirements.txt
```

### 代码风格

- 遵循PEP 8代码规范
- 类和函数使用文档字符串进行注释
- 关键逻辑添加清晰的注释说明

## 🤝 贡献指南

欢迎提交问题和改进建议！如果您想为项目贡献代码，请按照以下步骤：

1. Fork本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 许可证

本项目采用MIT许可证 - 详情请查看[LICENSE](LICENSE)文件

## 📧 联系方式

如有任何问题或建议，请联系项目维护者。