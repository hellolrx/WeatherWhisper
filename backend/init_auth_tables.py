#!/usr/bin/env python3
"""
认证系统数据库表初始化脚本
用于创建用户认证相关的数据库表
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine
from app.database.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import text

async def create_auth_tables():
    """使用现有数据库表结构"""
    try:
        print("🔧 正在检查现有数据库表结构...")
        
        # 只检查连接，不重新创建表
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ 数据库连接正常")
        
        print("✅ 使用现有数据库表结构")
        
        # 创建测试用户（可选）
        await create_test_user()
        
        print("🎉 认证系统数据库初始化完成！")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)

async def create_test_user():
    """创建测试用户"""
    try:
        from app.database.connection import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # 检查是否已存在测试用户
            result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE email = 'test@example.com'")
            )
            count = result.scalar()
            
            if count == 0:
                # 创建测试用户
                test_user = User(
                    email="test@example.com",
                    username="测试用户",
                    password_hash=get_password_hash("test123456"),
                    verification_code="123456",
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(test_user)
                await session.commit()
                
                print("👤 测试用户创建成功")
                print("   邮箱: test@example.com")
                print("   密码: test123456")
            else:
                print("ℹ️  测试用户已存在")
                
    except Exception as e:
        print(f"⚠️  创建测试用户失败: {e}")

async def check_database_connection():
    """检查数据库连接"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ 数据库连接正常")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 WeatherWhisper 认证系统数据库初始化")
    print("=" * 50)
    
    # 检查数据库连接
    if not await check_database_connection():
        print("请检查数据库配置和连接")
        sys.exit(1)
    
    # 创建认证表
    await create_auth_tables()
    
    print("\n📋 下一步操作:")
    print("1. 启动后端服务: python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload")
    print("2. 启动前端服务: cd frontend && npm run dev")
    print("3. 访问 http://localhost:3000 测试应用")

if __name__ == "__main__":
    asyncio.run(main()) 