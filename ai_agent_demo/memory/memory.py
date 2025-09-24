# -*- coding: utf-8 -*-
"""
@File    : memory.py
@Time    : 2025/9/25 15:14
@Desc    : 会话记忆管理模块，用于存储和管理对话历史 
"""
from langchain.memory import ConversationBufferWindowMemory

# 限制历史消息数量为10条，避免记忆无限增长
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=10)
