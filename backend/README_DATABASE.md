# WeatherWhisper 数据库设置指南

## 🗄️ 数据库配置

### 1. MySQL 安装和配置

#### 方法一：使用 Docker（推荐）
```bash
# 安装 Docker Desktop 后运行
docker run --name mysql-weatherwhisper \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=weatherwhisper \
  -p 3306:3306 \
  -d mysql:8.0
```

#### 方法二：本地安装
1. 从 [MySQL官网](https://dev.mysql.com/downloads/installer/) 下载安装包
2. 安装时设置 root 密码
3. 启动 MySQL 服务

### 2. 创建数据库
在 MySQL Workbench 或命令行中执行：
```sql
CREATE DATABASE weatherwhisper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE weatherwhisper;
```

### 3. 环境变量配置
确保 `backend/.env` 文件包含以下配置：
```env
# 数据库配置
DATABASE_URL=mysql+asyncmy://root:your_password@localhost:3306/weatherwhisper

# SMTP配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_qq_email@qq.com
SMTP_PASSWORD=your_smtp_authorization_code
SMTP_USE_TLS=true

# 和风天气API
QWEATHER_API_KEY=your_qweather_api_key

# 安全配置
SECRET_KEY=your_generated_secret_key

# 应用配置
DEBUG=true
```

## 🚀 运行项目

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_database.py
```

### 3. 启动应用
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 数据库表结构

### users 表
- 用户基本信息
- 邮箱验证状态
- 密码哈希

### cities 表
- 城市信息
- 搜索统计
- 坐标信息

### user_favorites 表
- 用户收藏的城市
- 收藏时间

### weather_cache 表
- 天气数据缓存
- 过期时间管理

### email_verifications 表
- 邮箱验证记录
- 验证码管理

## 🔧 故障排除

### 常见问题

1. **MySQL 连接失败**
   - 检查 MySQL 服务是否运行
   - 验证用户名和密码
   - 确认端口号（默认3306）

2. **权限不足**
   - 确保数据库用户有创建表的权限
   - 检查数据库是否存在

3. **SMTP 配置错误**
   - 验证 QQ 邮箱的 SMTP 授权码
   - 检查端口和 TLS 设置

4. **Secret Key 问题**
   - 生成新的安全密钥
   - 确保密钥长度足够（至少32字符）

### 生成 Secret Key
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📝 API 端点

### 认证相关
- `POST /api/auth/register/email` - 发送注册验证邮件
- `POST /api/auth/register/verify` - 验证邮箱验证码
- `POST /api/auth/register/complete` - 完成注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息

### 收藏城市
- `POST /api/favorites/add` - 添加收藏城市
- `DELETE /api/favorites/remove/{city_name}` - 移除收藏
- `GET /api/favorites/list` - 获取收藏列表
- `GET /api/favorites/popular` - 获取热门城市

## 🔄 数据库迁移

使用 Alembic 进行数据库迁移：
```bash
# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```
