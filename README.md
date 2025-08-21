# WeatherWhisper (天语)

一个基于 Vue3 + FastAPI 的本地天气应用，对接和风天气 API，支持城市搜索、多天气类型展示、本地收藏与智能穿衣建议。

## ✨ 核心功能

- 🌡️ **实时天气**: 当前温度、体感温度、风向风力、湿度等详细信息
- 📊 **天气预报**: 24小时逐时预报 + 7天趋势预报
- ⭐ **城市收藏**: 支持多城市管理，按省份分组显示
- 📧 **邮件推送**: 立即发送 / 定时推送天气到邮箱
- 🤖 **AI穿衣建议**: RAG + Gemini 生成个性化穿搭推荐
- 👤 **用户系统**: 注册登录、邮箱验证、JWT认证

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite 5
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP**: Axios
- **样式**: 原生 CSS（模块化）
- **存储**: localStorage（城市收藏）

### 后端
- **框架**: FastAPI
- **ASGI**: Uvicorn
- **HTTP Client**: HTTPX（异步）
- **缓存**: cachetools（TTLCache）
- **环境变量**: python-dotenv
- **数据校验**: Pydantic

### AI & RAG
- **向量数据库**: Pinecone（知识库存储与检索）
- **嵌入模型**: BAAI/bge-base-zh-v1.5（中文语义向量）
- **生成模型**: Google Gemini 1.5 Flash（穿衣建议生成）
- **知识库**: 时尚穿搭专业知识（CSV格式，自动向量化）

### 数据库 & 认证
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy（异步模式）
- **认证**: JWT + bcrypt（访问令牌7天，刷新令牌30天）
- **邮件服务**: QQ邮箱SMTP + 验证码系统

### 开发工具
- **包管理**: npm (前端) + pip (后端)
- **版本控制**: Git
- **内网穿透**: ngrok
- **IDE**: cursor

## 项目结构

### 🏗️ 模块化架构设计

项目采用组件化、模块化的架构设计，提高代码的可维护性和复用性：

```
WeatherWhisper/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由层
│   │   │   ├── geo.py     # 城市查询接口
│   │   │   ├── weather.py # 天气数据接口
│   │   │   ├── auth.py    # 认证相关接口
│   │   │   ├── favorites.py # 收藏城市接口
│   │   │   ├── notifications.py # 邮件通知接口
│   │   │   └── rag.py     # RAG穿衣建议接口
│   │   ├── services/
│   │   │   ├── qweather.py # 第三方API服务层
│   │   │   ├── auth_service.py # 认证服务
│   │   │   ├── notification_service.py # 邮件服务
│   │   │   ├── rag_service.py # RAG检索与生成服务
│   │   │   └── email_service.py # SMTP邮件发送
│   │   ├── database/       # 数据库层
│   │   │   ├── models/    # SQLAlchemy模型
│   │   │   └── connection.py # 数据库连接
│   │   └── main.py        # 应用入口
│   ├── rag/               # RAG相关文件
│   │   ├── knowledge_base.xlsx # 穿搭知识库（Excel格式）
│   │   ├── ingest_pinecone.py # 向量化入库脚本
│   │   └── test_gemini.py # Gemini API测试
│   ├── .env               # 环境变量配置
│   └── requirements.txt   # Python 依赖
└── frontend/              # Vue3 前端（模块化重构）
    ├── src/
    │   ├── components/     # 🧩 组件库
    │   │   ├── search/     # 搜索相关组件
    │   │   │   └── SearchBox.vue
    │   │   ├── favorites/  # 收藏功能组件
    │   │   │   └── FavoriteCities.vue
    │   │   ├── weather/    # 天气显示组件
    │   │   │   ├── CurrentWeather.vue
    │   │   │   ├── HourlyForecast.vue
    │   │   │   └── DailyForecast.vue
    │   │   ├── auth/       # 认证相关组件
    │   │   │   └── UserInfo.vue
    │   │   └── modals/     # 弹窗组件
    │   │       └── SendWeatherEmailModal.vue
    │   ├── composables/    # 🎣 组合式API
    │   │   ├── useWeatherApi.ts    # 天气API服务
    │   │   ├── useGeolocation.ts   # 地理位置服务
    │   │   ├── useAuth.ts          # 认证服务
    │   │   └── useNotificationApi.ts # 通知API服务
    │   ├── stores/         # 📦 状态管理
    │   │   ├── favorites.ts # 收藏城市Store
    │   │   └── auth.ts     # 认证状态Store
    │   ├── styles/         # 🎨 样式模块
    │   │   ├── global.css  # 全局样式重置
    │   │   ├── layout.css  # 布局样式
    │   │   └── cards.css   # 卡片组件样式
    │   ├── types/          # 📝 类型定义
    │   │   └── weather.ts  # 天气相关类型
    │   ├── utils/          # 🔧 工具函数
    │   │   ├── common.ts   # 通用工具函数
    │   │   ├── http.ts     # HTTP请求封装
    │   │   └── weather/    # 天气相关工具
    │   │       └── icons.ts # 天气图标映射
    │   ├── constants/      # 📋 常量管理
    │   │   └── index.ts    # 应用配置常量
    │   ├── views/          # 📄 页面组件
    │   │   └── Dashboard.vue # 主页面（新架构）
    │   └── main.ts         # 应用入口
    │   ├── router/
    │   └── App.vue
    ├── vite.config.ts     # Vite 配置（含代理）
    └── package.json       # Node 依赖

### 🎯 架构设计原则

- **组件化设计**: 单一职责、可复用、松耦合
- **样式模块化**: scoped样式 + CSS模块化管理
- **业务逻辑分层**: Composables + API服务层 + 工具函数
- **状态管理**: Pinia全局状态 + 组件局部状态
- **类型安全**: TypeScript类型定义确保数据结构一致性

### 🔧 开发工作流

新增功能时请遵循以下模式：
```bash
# 1. 新增组件
src/components/功能模块/ComponentName.vue

# 2. 新增业务逻辑
src/composables/useFeatureName.ts

# 3. 新增类型定义
src/types/featureName.ts
```

## 快速开始

### 1. 后端配置
```bash
# 1. 创建并激活虚拟环境
py -m venv backend\.venv
backend\.venv\Scripts\activate  # Windows
source backend/.venv/bin/activate  # Linux/Mac

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 配置 backend/.env

# 4. 启动后端（开发模式）
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

### 2. 前端配置
```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev
```

### 3. 验证
1. 打开 `http://127.0.0.1:8000/api/health` 检查后端
2. 访问 `http://localhost:3000` 使用应用
3. 在搜索框输入"北京"，选择下拉项即可看到天气信息

## API 接口

### 后端代理接口
- `GET /api/health` - 健康检查
- `GET /api/geo?query=城市名` - 城市搜索
- `GET /api/weather/now?location=城市ID` - 实时天气
- `GET /api/weather/24h?location=城市ID` - 24小时预报
- `GET /api/weather/7d?location=城市ID` - 7天预报

### 数据缓存
- 使用 TTLCache 对和风天气 API 响应做 60 秒缓存
- 缓存键：请求URL + 参数的稳定字符串
- 自动清理过期缓存

## 内网穿透（可选）
```bash
# 仅暴露前端 5173 端口（已配置代理）
ngrok http http://localhost:3000

# 复制生成的域名分享即可
# 形如 https://xxxx.ngrok-free.app
```

## 开发建议
1. **环境变量**
   - 严格遵守 `.gitignore`，不要提交 `.env` 文件
   - 参考 `.env.example` 配置本地环境

2. **API 调用**
   - 使用和风天气免费版 API（devapi/geoapi）
   - 若用专属域名（*.re.qweatherapi.com），需改用 Bearer 鉴权

3. **缓存策略**
   - 默认 60 秒 TTL 适合大多数场景
   - 可在 `qweather.py` 中调整缓存参数

4. **前端优化**
   - 搜索防抖（已实现）
   - 错误友好提示
   - 响应式设计
   - 模块化CSS架构

## Git 提交与推送流程

### 正确的提交步骤

#### 1. 检查文件状态
```bash
git status
```

#### 2. 创建提交
```bash
git commit -m ""
```
使用简洁明确的提交信息，遵循约定式提交格式。

#### 3. 推送到远程仓库
```bash
git push origin main
```

### 提交信息规范
- `feat:` - 新功能
- `fix:` - 修复bug
- `docs:` - 文档更新
- `style:` - 代码格式调整
- `refactor:` - 重构代码

## ✉️ 邮件推送天气（2025-08-19）

### 功能概览
- **立即发送**
  - 在"当前天气"与"已关注的城市"处新增"发送到邮箱"按钮
  - 弹窗支持选择城市、邮箱（默认登录邮箱，可改）、实时预览"今日天气摘要"后发送
  - 发送成功/失败，弹窗右上角 toast 提示（成功 1.2 秒后自动关闭）
- **定时发送**
  - 频率：一次 / 每天
  - 默认值：切换到"定时"时，频率默认"一次"，时间=当前时刻，日期=今天（Asia/Shanghai）
  - 创建成功后由后台调度器自动在到点执行

### 技术实现
- **后端**
  - FastAPI + SQLAlchemy Async（MySQL / asyncmy）
  - 邮件发送：`emails` 库（QQ SMTP）
  - 天气数据：和风天气 API（实时 + 7 天）；预览文案由服务层组合（"今日实时 + 今日高低温"）
  - 轻量调度器：`EmailScheduleWorker`（后台异步循环，每 60 秒扫描一次）
    - 到期任务执行发送；ONCE 成功后置 `SENT`；DAILY 成功后 `next_run_at += 1 day`
    - 失败任务回退 5 分钟后重试，避免热循环
  - 通知路由：优先支持 `city_name + province` 入参；服务内自动解析和风 `location id`
- **前端**
  - 弹窗 `SendWeatherEmailModal`：城市下拉、邮箱、发送方式（立即/定时）、频率/时间/日期、预览区、loading 与 toast
  - API 封装 `useNotificationApi`：`previewWeatherEmail / sendWeatherEmail / scheduleWeatherEmail`
  - 收藏点击后通过"省份+城市名"解析出和风城市 ID 再查询天气，避免 ID 缺失

### 数据库存储
- `email_notifications`：发送日志
  - 关键字段：`user_id, email, city_id, subject, content, status(SENT/FAILED), error_message, created_at`
- `email_schedules`：定时任务
  - 关键字段：`user_id, email, city_id, city_name, province, type(ONCE|DAILY), time_hhmm, date, timezone, next_run_at(UTC), status(ACTIVE/CANCELLED/SENT), last_run_at, created_at`

### 使用说明
- **立即发送**
  1. 点击"发送到邮箱"打开弹窗，确认城市与邮箱
  2. 预览区展示"今日天气摘要"，点击"发送"
  3. 弹窗右上角显示结果；成功 1.2 秒后自动关闭
  4. 可在 `email_notifications` 表查看历史记录
- **创建定时**
  1. 切换"定时"，设置"频率/时间/日期"（默认已填好）
  2. 点击"创建定时"，成功后由后台每 60 秒扫描，到点自动发送
  3. ONCE 执行成功后任务标记为 `SENT`；DAILY 执行成功后 `next_run_at += 1 天`

## 🤖 RAG 智能穿衣建议（2025-08-21）

### 功能概览
- **AI穿衣建议**: 基于实时天气数据生成个性化穿搭建议
- **无缝集成**: 在邮件预览/发送中自动附加穿衣建议
- **专业指导**: 考虑温差、湿度、风力等多维度因素

### 技术架构
- **向量数据库**: Pinecone（云端向量检索）
- **嵌入模型**: BAAI/bge-base-zh-v1.5（中文语义向量）
- **生成模型**: Google Gemini 1.5 Flash（快速响应）
- **知识库**: 专业穿搭知识（Excel格式，自动向量化）

### 核心流程
```
天气数据提取 → 语义查询构建 → 向量检索 → AI生成 → 穿衣建议
```

### 环境配置
```bash
# backend/.env
PINECONE_API_KEY=your_pinecone_key
GEMINI_API_KEY=your_gemini_key

# 向量化知识库
python backend/rag/ingest_pinecone.py
```

### API 接口
- **邮件集成**: 预览/发送时自动生成穿衣建议
- **独立接口**: `GET /api/fashion-advice?city_id=xxx&city_name=xxx`