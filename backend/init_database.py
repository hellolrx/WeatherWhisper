#!/usr/bin/env python3
"""
数据库初始化脚本
用于手动创建数据库和表结构
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import init_db, close_db
from app.core.config import settings


async def main():
    """主函数"""
    print("🚀 开始初始化数据库...")
    print(f"📊 数据库URL: {settings.database_url}")
    
    try:
        # 初始化数据库
        await init_db()
        print("✅ 数据库初始化成功！")
        
        # 显示配置信息
        print("\n📋 配置信息:")
        print(f"   数据库: {settings.database_url}")
        print(f"   SMTP主机: {settings.smtp_host}")
        print(f"   SMTP端口: {settings.smtp_port}")
        print(f"   SMTP用户: {settings.smtp_user}")
        print(f"   和风天气API: {'已配置' if settings.qweather_api_key else '未配置'}")
        print(f"   密钥: {'已配置' if settings.secret_key != 'your-secret-key-here' else '未配置'}")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查MySQL服务是否运行")
        print("2. 检查数据库连接信息是否正确")
        print("3. 确保数据库用户有创建表的权限")
        print("4. 检查.env文件中的配置")
        return 1
    
    finally:
        # 关闭数据库连接
        await close_db()
        print("\n🔒 数据库连接已关闭")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
