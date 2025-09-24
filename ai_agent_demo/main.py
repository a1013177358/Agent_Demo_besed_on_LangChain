# -*- coding: utf-8 -*-
"""
@File    : main.py
@Time    : 2025/9/25 15:12
@Desc    : 项目主入口文件 
"""
import os
from dotenv import load_dotenv
from agents.base_agent import build_agent
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# 加载.env文件中的环境变量，明确指定.env文件路径
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 确保GOOGLE_API_KEY环境变量被设置
if not os.getenv('GOOGLE_API_KEY'):
    print("⚠️ 警告: 未设置GOOGLE_API_KEY环境变量。")
    print("请在.env文件中配置您的API密钥，格式为: GOOGLE_API_KEY=your_api_key_here")


def run():
    agent = build_agent()

    print("🔧 智能体已启动... 输入 exit 退出")

    while True:
        user_input = input("\n🧑 用户: ")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 再见！")
            break
        
        # 使用正确的格式调用智能体
        try:
            # 对于我们的SimpleToolAgent，直接传递用户输入
            response = agent.invoke(user_input)
            print(f"\n🤖 Agent: {response}")
        except Exception as e:
            print(f"\n❌ 处理请求时出错: {str(e)}")


if __name__ == "__main__":
    run()
