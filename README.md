# Agent Demo 项目简介

这是一个基于大语言模型的智能体演示项目，集成了知识库检索、网络搜索和多模态理解能力，提供命令行和Web界面两种交互方式。

## 项目特点

- **本地知识库**：支持PDF/TXT/DOCX格式文档的向量化存储和语义检索
- **实时信息获取**：集成Tavily搜索API，获取最新网络信息
- **多模态理解**：支持图像内容分析与描述生成
- **上下文记忆**：记住对话历史，提供连贯的交流体验
- **双界面支持**：提供命令行和Web界面两种交互方式

## 目录结构

```
Agent Demo预发布/
├── ai_agent_demo/      # 主项目目录
│   ├── README.md       # 详细项目文档
│   ├── LICENSE         # 许可证文件
│   ├── main.py         # 命令行模式入口
│   ├── app/            # Web应用部分
│   ├── agents/         # 智能体实现
│   ├── tools/          # 工具函数
│   ├── memory/         # 会话记忆管理
│   ├── multimodal/     # 多模态处理
│   └── knowledge_base/ # 知识库文件
└── README.md           # 项目简介
```

## 快速开始

请参考 `ai_agent_demo/README.md` 文件获取详细的安装和使用说明。

主要步骤包括：
1. 安装依赖：`pip install -r ai_agent_demo/requirements.txt`
2. 配置API密钥（Google Gemini和Tavily）
3. 启动服务（命令行或Web界面）
## 许可证

本项目采用MIT许可证 - 详情请查看 `ai_agent_demo/LICENSE` 文件。
