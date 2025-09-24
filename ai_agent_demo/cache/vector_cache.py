# -*- coding: utf-8 -*-
"""
@File    : vector_cache.py
@Time    : 2025/9/25 15:00
@Desc    : 向量存储缓存模块，用于缓存已构建的文档向量存储，避免重复构建
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 全局向量存储缓存
vectorstore_cache = {}