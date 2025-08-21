# WeatherWhisper 问题记录与解决方案

> 本文档记录了 WeatherWhisper 项目开发过程中遇到的主要问题和解决方案，供开发者参考。

## 🗂️ 目录

- [环境配置问题](#环境配置问题)
- [依赖管理问题](#依赖管理问题)
- [数据库连接问题](#数据库连接问题)
- [前端样式问题](#前端样式问题)
- [认证系统问题](#认证系统问题)
- [RAG功能问题](#rag功能问题)
- [部署相关问题](#部署相关问题)

## 环境配置问题

### 1. Python路径配置错误

**问题描述：**
```
No Python at '"D:\python312\python.exe'
```

**问题原因：**
- 虚拟环境配置指向了不存在的Python路径
- 系统中有多个Python版本，虚拟环境指向错误版本

**解决方案：**
```bash
# 删除损坏的虚拟环境
deactivate
Remove-Item -Path "backend\.venv" -Recurse -Force

# 重新创建虚拟环境
py -m venv backend\.venv
backend\.venv\Scripts\activate

# 重新安装依赖
pip install -r backend/requirements.txt
```

### 2. requirements.txt编码问题

**问题描述：**
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0xae in position 27: illegal multibyte sequence
```

**问题原因：**
- Windows系统默认使用GBK编码读取文件
- requirements.txt文件包含中文字符
- pip无法正确解析文件内容

**解决方案：**
- 将requirements.txt中的中文注释改为英文
- 使用UTF-8编码保存文件
- 避免在配置文件中使用特殊字符

## 依赖管理问题

### 1. pip依赖冲突

**问题描述：**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
mcp 1.9.1 requires anyio>=4.5, but you have anyio 3.7.1 which is incompatible.
mcp 1.9.1 requires pydantic<3.0.0,>=2.7.2, but you have pydantic 2.5.0 which is incompatible.
```

**解决方案：**
```bash
# 升级冲突的包到兼容版本
pip install "anyio>=4.5"
pip install "pydantic>=2.7.2"
pip install "starlette>=0.41.3"
pip install "h11>=0.16.0"
```

**预防措施：**
- 使用虚拟环境隔离项目依赖
- 定期更新requirements.txt文件
- 避免在系统Python中安装过多包

### 2. JWT模块导入错误

**问题描述：**
```
ModuleNotFoundError: No module named 'jwt'
```

**问题原因：**
- 代码中使用了 `import jwt`
- 但应该使用 `python-jose` 包提供的JWT功能

**解决方案：**
```python
# 修复前
import jwt

# 修复后
from jose import jwt, JWTError

# 同时修复异常处理
# 修复前
except jwt.PyJWTError:
# 修复后
except JWTError:
```

### 3. pydantic-settings模块缺失

**问题描述：**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**解决方案：**
```bash
# 安装pydantic-settings
pip install pydantic-settings

# 或者使用兼容的导入方式
from pydantic import BaseSettings  # 对于pydantic v2
```

## 数据库连接问题

### 1. MySQL连接认证失败

**问题描述：**
```
ERROR:app.database.connection:Database initialization error: (asyncmy.errors.OperationalError) (1045, "Access denied for user 'root'@'localhost' (using password: YES)")
```

**问题原因：**
- MySQL用户密码配置错误
- 认证插件不兼容（caching_sha2_password vs mysql_native_password）

**解决方案：**
```sql
-- 创建新用户，使用兼容的认证方式
CREATE USER 'weatheruser'@'localhost' IDENTIFIED BY 'weatherpass123';
GRANT ALL PRIVILEGES ON weatherwhisper.* TO 'weatheruser'@'localhost';
GRANT ALL PRIVILEGES ON weatherwhisper.* TO 'weatheruser'@'127.0.0.1';
FLUSH PRIVILEGES;
```

**更新.env文件：**
```bash
DATABASE_URL=mysql+asyncmy://weatheruser:weatherpass123@localhost:3306/weatherwhisper
```

### 2. 缺失的数据库模型文件

**问题描述：**
```
ModuleNotFoundError: No module named 'app.schemas.user'
```

**解决方案：**
创建缺失的模块文件：
- `backend/app/schemas/user.py` - 用户数据模型
- `backend/app/schemas/city.py` - 城市数据模型  
- `backend/app/schemas/weather.py` - 天气数据模型

### 3. 数据库表结构不匹配

**问题描述：**
```
Unknown column 'city_name' in 'field list'
```

**解决方案：**
```sql
-- 补齐缺失的列
ALTER TABLE email_schedules ADD COLUMN IF NOT EXISTS city_name VARCHAR(100) NULL;
ALTER TABLE email_schedules ADD COLUMN IF NOT EXISTS province VARCHAR(100) NULL;
```

## 前端样式问题

### 1. TypeScript 找不到已删除文件错误

**问题症状：**
```
找不到文件"d:/WeatherWhisper/frontend/src/components/HelloWorld.vue"。
程序包含该文件是因为:
  通过在 "d:/WeatherWhisper/frontend/tsconfig.app.json" 中的包含模式 "src/**/*.vue" 匹配
```

**解决方案：**
```bash
# 方法1：清理 TypeScript 构建缓存
cd frontend
Remove-Item -Path "node_modules/.tmp" -Recurse -Force -ErrorAction SilentlyContinue

# 方法2：重启 TypeScript 语言服务
# 在 VS Code/Cursor 中：
# 1. 按 Ctrl+Shift+P 打开命令面板
# 2. 输入 "TypeScript: Restart TS Server"
# 3. 选择并执行

# 方法3：重新构建项目
npm run build
```

### 2. 背景无法全屏问题

**问题**：页面背景出现白边，无法覆盖整个屏幕

**解决方案：**
```css
/* ✅ 解决方案 */
html, body {
  margin: 0;
  padding: 0;
}

body {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 50%, #6c5ce7 100%);
  background-attachment: fixed; /* 关键：固定背景 */
  background-size: cover; /* 覆盖整个视口 */
  min-height: 100vh;
}

.container {
  margin: 0 auto;
  padding: clamp(0.5rem, 1vw, 1.5rem); /* 容器内边距 */
}
```

### 3. 内容溢出和布局混乱

**问题**：卡片内容溢出容器，横向滚动失效

**解决方案：**
```css
/* ✅ 解决方案 */
.hourly-forecast-module {
  display: grid;
  grid-template-columns: repeat(6, 1fr); /* 桌面端：6列网格 */
  gap: clamp(1rem, 2vw, 1.5rem);
  justify-items: center;
}

@media (max-width: 767px) {
  .hourly-forecast-module {
    grid-template-columns: repeat(4, 1fr); /* 移动端：4列网格 */
  }
}
```

### 4. 下拉框遮挡问题

**问题**：搜索下拉框与收藏列表重叠

**解决方案：**
```css
/* 下拉框使用绝对定位 */
.options-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  z-index: 2000;
}

/* 收藏框动态推移 */
.favorites-section.pushed-down {
  margin-top: 280px;
  transition: margin-top 0.3s ease;
}
```

## 认证系统问题

### 1. JWT令牌验证失败

**问题描述：**
- 用户登录后访问受保护接口返回401
- 前端存储的token无法通过后端验证

**解决方案：**
1. 检查JWT密钥配置
2. 确认token格式正确（Bearer前缀）
3. 验证token过期时间设置

### 2. 邮箱验证码发送失败

**问题描述：**
- SMTP连接超时
- 邮件服务商认证失败

**解决方案：**
```bash
# 确认QQ邮箱SMTP配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_smtp_password  # QQ邮箱授权码，非登录密码
SMTP_USE_TLS=true
```

## RAG功能问题

### 1. Pinecone连接失败

**问题描述：**
```
RuntimeError: PINECONE_API_KEY 未配置
```

**解决方案：**
```bash
# 在 backend/.env 添加
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
```

### 2. 向量化入库失败

**问题描述：**
- Excel文件读取失败
- 向量维度不匹配

**解决方案：**
```bash
# 确认Excel文件格式
# 必需列：id, category, suggestion

# 重新执行向量化
python backend/rag/ingest_pinecone.py
```

### 3. Gemini API调用超时

**问题描述：**
- 生成建议时间过长
- API配额超限

**解决方案：**
1. 增加前端请求超时时间
2. 使用更快的模型（gemini-1.5-flash）
3. 实现降级策略

## 部署相关问题

### 1. 环境变量配置优先级

**问题描述：**
- 修改了 `config.py` 中的默认值
- 但 `.env` 文件中的配置仍然覆盖了默认值

**解决方案：**
1. 更新 `.env` 文件中的配置
2. 确保 `config.py` 中的默认值也是正确的
3. 使用环境变量覆盖默认值

### 2. 静态文件访问问题

**问题描述：**
- 前端构建后的静态文件无法访问
- 接口代理配置错误

**解决方案：**
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## 🎯 成功启动检查清单

### 后端启动检查
- [x] 虚拟环境激活
- [x] 依赖包安装完成
- [x] 数据库连接成功
- [x] 数据库表创建成功
- [x] FastAPI服务启动成功
- [x] 端口8000监听正常
- [x] 认证API接口正常
- [x] JWT令牌生成验证正常

### 前端启动检查
- [x] Node.js环境正常
- [x] 依赖包安装完成
- [x] 开发服务器启动成功
- [x] 端口3000监听正常
- [x] 代理配置正确
- [x] 登录注册页面正常
- [x] 路由守卫正常工作

### 数据库配置检查
- [x] MySQL服务运行正常
- [x] 数据库用户权限正确
- [x] 数据库表结构完整
- [x] 连接字符串格式正确
- [x] 外键约束配置正确
- [x] 级联删除规则正常

### RAG功能检查
- [x] Pinecone索引存在
- [x] 知识库向量化完成
- [x] Gemini API配置正确
- [x] 嵌入模型下载完成

## 💡 开发经验总结

1. **环境隔离很重要**：使用虚拟环境避免系统包冲突
2. **配置文件要同步**：代码默认值和环境变量要保持一致
3. **依赖版本要兼容**：注意包之间的版本兼容性
4. **错误信息要仔细看**：很多问题都有明确的错误提示
5. **分步骤解决问题**：一次解决一个问题，避免同时修改多个地方
6. **数据库外键设计**：合理设计外键约束，使用级联删除避免数据不一致
7. **ORM模型同步**：确保SQLAlchemy模型与数据库表结构完全匹配
8. **认证流程设计**：JWT令牌过期时间要合理，前端存储要安全
9. **错误处理机制**：友好的错误提示和异常处理提升用户体验
10. **代码架构清晰**：前后端分离，模块化设计便于维护和扩展

## 🔧 调试命令参考

```bash
# Python环境调试
python --version                         # 检查Python版本
pip list                                 # 查看已安装包
pip check                               # 检查依赖冲突

# 数据库调试
mysql -u weatheruser -p                 # 连接数据库
SHOW TABLES;                            # 查看表结构
DESCRIBE table_name;                    # 查看表字段

# 服务调试
netstat -ano | findstr :8000           # 检查端口占用
ps aux | grep uvicorn                  # 检查进程状态

# 前端调试
npm run build                           # 构建检查
npm run type-check                      # 类型检查

# 缓存清理
Remove-Item -Path "__pycache__" -Recurse -Force  # 清理Python缓存
Remove-Item -Path "node_modules/.cache" -Recurse -Force  # 清理Node缓存
```

---

> 如遇到文档中未记录的问题，请及时补充到对应章节，保持文档的完整性和实用性。 