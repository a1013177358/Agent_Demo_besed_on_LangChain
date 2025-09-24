# 首先设置全局日志级别，在导入任何其他模块之前
import os
import sys
import logging
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"
# 如果有 TensorFlow / JAX 的日志，也屏蔽掉 info 和 warning
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
# 抑制所有Google相关的警告

from langchain_google_genai import ChatGoogleGenerativeAI

# 从环境变量加载API密钥，如果没有设置则提示用户
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ 警告: 未设置GOOGLE_API_KEY环境变量。")
    print("请在.env文件中配置您的API密钥，格式为: GOOGLE_API_KEY=your_api_key_here")
    sys.exit(1)

# 配置ChatGoogleGenerativeAI参数
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    max_tokens=None,
    timeout=30,
    max_retries=2,
)

# 准备测试消息
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]

# 添加异常处理
try:
    ai_msg = llm.invoke(messages)
    print("成功获取响应!")
    print(f"响应内容: {ai_msg}")
except Exception as e:
    print(f"发生错误: {type(e).__name__}: {str(e)}")
    print("请检查以下几点:")
    print("1. API密钥是否正确")
    print("2. 网络连接是否正常")
    print("3. 防火墙是否阻止了连接")