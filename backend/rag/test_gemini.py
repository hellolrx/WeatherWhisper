import os
from dotenv import load_dotenv
import google.generativeai as genai

# 加载 .env 文件中的环境变量
load_dotenv()

# 配置 Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("错误：请在 .env 文件中设置 GEMINI_API_KEY")
else:
    genai.configure(api_key=GEMINI_API_KEY)

    try:
        # 创建一个模型实例
        model = genai.GenerativeModel('gemini-1.5-flash') # 使用最新的或适合的模型

        # 发送一个简单的请求
        print("正在向 Gemini API 发送测试请求...")
        response = model.generate_content("今晚吃啥")

        # 打印返回结果
        print("\nGemini API 返回成功！")
        print("回复内容:", response.text)

    except Exception as e:
        print(f"\n调用 Gemini API 时发生错误: {e}")
        print("请检查：\n1. 您的 API Key 是否正确且已启用。\n2. 您的网络是否可以访问 Google 服务。")