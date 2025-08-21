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

#### 1. **组件化设计**
- **单一职责**: 每个组件只负责一个特定功能
- **可复用性**: 组件设计考虑在不同场景下的复用
- **松耦合**: 组件间通过props和events通信，避免直接依赖

#### 2. **样式模块化**
- **全局样式**: `styles/global.css` - 重置样式和基础设定
- **布局样式**: `styles/layout.css` - 网格布局和响应式设计
- **组件样式**: 每个组件使用scoped样式，避免样式污染
- **样式复用**: 通用卡片、按钮等基础样式提取为CSS模块

#### 3. **业务逻辑分层**
- **Composables**: 使用Vue3组合式API封装可复用的业务逻辑
- **API服务层**: `composables/useWeatherApi.ts` 统一管理API调用
- **工具函数**: `utils/` 目录存放纯函数工具
- **类型安全**: TypeScript类型定义确保数据结构一致性

#### 4. **状态管理**
- **Store模式**: 使用Pinia管理全局状态（如收藏城市）
- **局部状态**: 组件内部状态使用ref/reactive
- **数据持久化**: localStorage集成在Store中，统一管理

#### 5. **可维护性原则**
- **文件职责明确**: 每个文件只负责特定功能
- **命名规范**: 组件、函数、变量使用语义化命名
- **配置集中**: 常量和配置统一管理在`constants/`
- **文档完整**: 关键函数和组件包含TypeScript类型注释

### 🚀 使用新架构的好处

1. **开发效率提升**: 组件化开发，功能模块独立，并行开发更容易
2. **维护成本降低**: 单个组件修改不影响其他部分，降低回归风险
3. **代码复用性**: 组件可在不同页面复用，减少重复代码
4. **团队协作**: 清晰的文件结构和职责分工，便于多人协作
5. **测试友好**: 每个组件和函数都可以独立测试
6. **扩展性强**: 新增功能只需添加新组件，不需修改现有代码

### 💡 **架构迁移说明**

**重要提示：项目已完成架构重构！** 

- ✅ **旧版本**: 单一 `Dashboard.vue` 文件（已删除）
- 🚀 **新版本**: 模块化组件架构（当前使用）

如果您是协作者，请注意：
1. 项目现在使用模块化架构，代码更清晰易维护
2. 所有功能已拆分为独立组件，在 `src/components/` 目录
3. 业务逻辑提取为 `composables`，样式模块化管理
4. 如有疑问，请参考上面的架构设计原则

### 🔧 **开发工作流**

新增功能时请遵循以下模式：
```bash
# 1. 新增组件
src/components/功能模块/ComponentName.vue

# 2. 新增业务逻辑
src/composables/useFeatureName.ts

# 3. 新增类型定义
src/types/featureName.ts

# 4. 新增样式模块（可选）
src/styles/featureName.css
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
QWEATHER_API_KEY=你的和风天气密钥
QWEATHER_GEO=https://geoapi.qweather.com
QWEATHER_BASE=https://devapi.qweather.com
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 4. 启动后端（开发模式）
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

### 2. 前端配置
```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev -- --host 0.0.0.0 --port 5173
```

### 3. 验证
1. 打开 `http://127.0.0.1:8000/api/health` 检查后端
2. 访问 `http://localhost:5173` 使用应用
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
ngrok http http://localhost:5173

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

## 前端设计规则

### CSS架构原则
1. **模块化设计**
   - 每个组件拥有独立的CSS样式
   - 避免使用 `!important` 强制覆盖
   - 明确的命名规范：`/* 组件名称样式 - 独立模块 */`

2. **样式隔离**
   ```css
   /* ✅ 推荐：组件独立样式 */
   .search-input {
     margin: 0;
     padding: clamp(1rem, 2.5vw, 1.5rem) clamp(1.5rem, 3vw, 2rem);
   }
   
   /* ❌ 避免：全局强制重置 */
   * {
     padding: 0 !important;
   }
   ```

3. **响应式设计**
   - 使用 `clamp()` 函数实现流体排版
   - 移动优先的响应式断点
   - Grid + Flexbox 混合布局

### 常见问题解决方案

#### 1. TypeScript 找不到已删除文件错误
**问题症状**：
```
找不到文件"d:/WeatherWhisper/frontend/src/components/HelloWorld.vue"。
程序包含该文件是因为:
  通过在 "d:/WeatherWhisper/frontend/tsconfig.app.json" 中的包含模式 "src/**/*.vue" 匹配
```

**问题原因**：TypeScript 编译器缓存中保留了对已删除文件的引用

**解决方案**：
```bash
# 方法1：清理 TypeScript 构建缓存
cd frontend
Remove-Item -Path "node_modules/.tmp" -Recurse -Force -ErrorAction SilentlyContinue

# 方法2：如果问题仍存在，重启 TypeScript 语言服务
# 在 VS Code/Cursor 中：
# 1. 按 Ctrl+Shift+P 打开命令面板
# 2. 输入 "TypeScript: Restart TS Server"
# 3. 选择并执行

# 方法3：重新构建项目
npm run build
```

**预防措施**：
- 删除组件文件后及时重启编辑器的 TypeScript 服务
- 定期清理构建缓存，特别是重构后
- 使用 `npm run build` 验证没有 TypeScript 错误

#### 2. 背景无法全屏问题
**问题**：页面背景出现白边，无法覆盖整个屏幕
```css
/* ❌ 问题代码 */
.app {
  padding: 2rem; /* 导致背景缩小 */
  background-size: 100% 100%; /* 固定尺寸，滚动时丢失 */
}
```

**解决方案**：
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

#### 2. 内容溢出和布局混乱
**问题**：卡片内容溢出容器，横向滚动失效
```css
/* ❌ 问题代码 */
.hour-cards {
  display: flex;
  flex-wrap: wrap; /* 导致换行而非滚动 */
}
```

**解决方案**：
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

#### 3. 文字贴边问题
**问题**：组件内文字紧贴边框，视觉效果差
```css
/* ❌ 问题代码 */
.card {
  padding: 0; /* 无内边距 */
}
```

**解决方案**：
```css
/* ✅ 解决方案：分组件独立设置 */
.search-input {
  padding: clamp(1rem, 2.5vw, 1.5rem) clamp(1.5rem, 3vw, 2rem);
}

.favorite-card {
  padding: 1rem 1.25rem;
}

.hour-card {
  padding: 1.25rem 1rem;
}
```

#### 4. 下拉框遮挡问题
**问题**：搜索下拉框与收藏列表重叠
**解决方案**：
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

### 开发最佳实践
1. **CSS优先级管理**
   - 避免深层嵌套选择器
   - 使用类选择器而非标签选择器
   - 只在必要时使用 `!important`

2. **布局调试技巧**
   - 使用浏览器开发者工具实时调试
   - 通过 `outline: 1px solid red` 快速定位问题
   - 检查 `box-sizing: border-box` 设置

3. **响应式测试**
   - 测试多种屏幕尺寸
   - 验证 `clamp()` 函数的最小/最大值
   - 确保触摸设备的交互友好性

## Git 提交与推送流程

### 正确的提交步骤

#### 1. 检查文件状态
```bash
git status
```
查看当前工作目录的修改状态，了解哪些文件已修改、新增或删除。

#### 2. 理解 .gitignore 规则
在提交前，务必了解 `.gitignore` 文件排除的内容：

**项目根目录 .gitignore 排除：**
- `backend/.venv/` - Python 虚拟环境
- `__pycache__/`, `*.pyc` - Python 编译文件
- `frontend/node_modules/` - Node.js 依赖包
- `backend/.env`, `.env` - 环境变量文件（包含敏感信息）
- `frontend/dist/` - 构建输出目录
- `.idea/`, `.vscode/` - IDE 配置文件
- 各种日志文件和系统文件

**frontend/.gitignore 补充排除：**
- `logs`, `*.log` - 日志文件
- `node_modules`, `dist` - 依赖和构建文件
- 编辑器临时文件


#### 4. 确认暂存区内容
```bash
git status
```
检查 "Changes to be committed" 部分，确保只包含应该提交的文件。

#### 5. 创建提交
```bash
git commit -m "feat: 更新天气应用功能和前端组件"
```
使用简洁明确的提交信息，遵循约定式提交格式。

#### 6. 推送到远程仓库
```bash
# 检查远程仓库配置
git remote -v

# 推送到 GitHub
git push origin main
```

#### 7. 验证推送结果
```bash
git status
# 应显示：Your branch is up to date with 'origin/main'
```

### 提交信息规范

采用约定式提交格式：
- `feat:` - 新功能
- `fix:` - 修复bug
- `docs:` - 文档更新
- `style:` - 代码格式调整
- `refactor:` - 重构代码
- `test:` - 测试相关
- `chore:` - 构建或辅助工具变动

### 常见错误避免

1. **不要提交敏感信息**
   - 环境变量文件（`.env`）
   - API 密钥和配置

2. **不要提交生成文件**
   - `node_modules/` - 依赖包目录
   - `dist/` - 构建输出
   - `__pycache__/` - Python 缓存

3. **不要提交IDE配置**
   - `.idea/`, `.vscode/` - 编辑器配置
   - 临时文件和缓存

### 最佳实践

1. **定期提交**：完成一个功能模块就提交一次
2. **原子提交**：每次提交只包含相关的更改
3. **清晰描述**：提交信息要能清楚说明本次更改的内容
4. **先拉后推**：多人协作时先 `git pull` 再 `git push`

## 许可说明
- 本项目仅用于学习交流
- 请遵守和风天气开发者协议
- 图标版权归和风天气所有

---

## 🚨 问题解决记录2025.8.11

本文档记录了项目启动过程中遇到的主要问题和解决方案，供后续开发者参考。

## 🎉 登录功能开发完成记录 2025.8.14

### 功能概述
✅ **用户注册**: 邮箱+用户名+密码（8位以上）+ 邮箱验证码验证  
✅ **用户登录**: 邮箱+密码+记住我功能  
✅ **访客模式**: 无需注册，直接进入天气主页
✅ **JWT认证**: 访问令牌7天，刷新令牌30天
✅ **安全特性**: 密码哈希存储，邮箱验证
✅ **邮箱验证**: QQ邮箱SMTP服务，6位数字验证码，10分钟有效期 ✅ **已完成并测试通过**

### 技术实现
- **后端**: FastAPI + SQLAlchemy + JWT + bcrypt + QQ邮箱SMTP
- **前端**: Vue3 + TypeScript + Pinia + Vue Router
- **数据库**: MySQL + 外键约束 + 级联删除
- **认证**: JWT令牌 + 本地存储 + 路由守卫
- **邮件服务**: QQ邮箱SMTP + 验证码生成 + 邮件模板

### 邮箱验证流程 ✅ **已实现**
1. **发送验证码**: 用户输入邮箱后点击"发送验证码" ✅
2. **验证码生成**: 系统生成6位数字验证码，有效期10分钟 ✅
3. **邮件发送**: 通过QQ邮箱SMTP服务发送验证码到用户邮箱 ✅
4. **验证码验证**: 用户输入验证码，系统验证后完成注册 ✅
5. **防重复发送**: 60秒倒计时，防止频繁发送验证码 ✅

### 邮箱配置说明 ✅ **已配置完成**
项目使用QQ邮箱SMTP服务发送验证码邮件，配置已完成：

```bash
# 在 backend/.env 文件中已配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_smtp_password  # QQ邮箱授权码，非登录密码
SMTP_USE_TLS=true
```

**获取QQ邮箱授权码步骤：**
1. 登录QQ邮箱网页版
2. 进入"设置" → "账户"
3. 开启"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 生成授权码（16位字符）
5. 将授权码填入 `SMTP_PASSWORD` 字段

### 数据库架构
- `users`: 用户基本信息、密码哈希、验证状态
- `user_favorites`: 用户收藏城市（外键关联）
- `weather_cache`: 天气数据缓存（外键关联）
- `email_verifications`: 邮箱验证码管理（新增）✅
- `password_reset_tokens`: 密码重置令牌
- `login_attempts`: 登录尝试记录
- `cities`: 城市信息管理

### 新增API接口 ✅ **已实现并测试**
- `POST /api/auth/send-verification` - 发送邮箱验证码 ✅
- `POST /api/auth/verify-code` - 验证邮箱验证码 ✅
- `POST /api/auth/register` - 用户注册（需要验证码）✅

### 前端功能增强 ✅ **已实现**
- **验证码发送按钮**: 带60秒倒计时，防止重复发送 ✅
- **验证码输入框**: 6位数字验证，实时格式验证 ✅
- **成功提示**: 验证码发送成功后的友好提示 ✅
- **表单验证**: 完整的表单验证逻辑，包括验证码验证 ✅
- **响应式设计**: 移动端友好的验证码发送按钮布局 ✅

### 🎯 **功能测试状态**
- ✅ 邮箱验证码发送功能正常
- ✅ 用户注册流程完整
- ✅ 前端验证码界面正常
- ✅ 后端API接口正常
- ✅ 数据库表结构完整
- ✅ SMTP配置正确

### 🚀 **下一步计划**
- [ ] 密码重置功能（使用邮箱验证）
- [ ] 用户资料管理
- [ ] 邮箱验证码重发优化
- [ ] 邮件模板美化

### 问题1：pip依赖冲突

**问题描述：**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
mcp 1.9.1 requires anyio>=4.5, but you have anyio 3.7.1 which is incompatible.
mcp 1.9.1 requires pydantic<3.0.0,>=2.7.2, but you have pydantic 2.5.0 which is incompatible.
```

**问题原因：**
- 系统Python环境中有多个包版本冲突
- 虚拟环境创建时继承了系统包的版本

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

### 问题2：Python路径配置错误

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

### 问题3：requirements.txt编码问题

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

**修复后的requirements.txt：**
```txt
# Core framework - compatible versions
fastapi>=0.104.0,<0.112.0
uvicorn[standard]>=0.24.0,<0.31.0
httpx>=0.25.0,<0.28.0
# ... 其他依赖
```

### 问题4：JWT模块导入错误

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

**需要修复的文件：**
- `backend/app/routers/auth.py`
- `backend/app/services/user_service.py`

### 问题5：pydantic-settings模块缺失

**问题描述：**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**问题原因：**
- 缺少 `pydantic-settings` 包
- 或者版本不兼容

**解决方案：**
```bash
# 安装pydantic-settings
pip install pydantic-settings

# 或者使用兼容的导入方式
from pydantic import BaseSettings  # 对于pydantic v2
```

### 问题6：数据库连接配置问题

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

### 问题7：缺失的数据库模型文件

**问题描述：**
```
ModuleNotFoundError: No module named 'app.schemas.user'
```

**问题原因：**
- 项目架构需要特定的数据模型文件
- 这些文件在项目迁移过程中丢失

**解决方案：**
创建缺失的模块文件：
- `backend/app/schemas/user.py` - 用户数据模型
- `backend/app/schemas/city.py` - 城市数据模型  
- `backend/app/schemas/weather.py` - 天气数据模型

### 问题8：环境变量配置优先级

**问题描述：**
- 修改了 `config.py` 中的默认值
- 但 `.env` 文件中的配置仍然覆盖了默认值

**问题原因：**
- `.env` 文件的配置优先级高于代码中的默认值
- 需要同时更新两个地方的配置

**解决方案：**
1. 更新 `.env` 文件中的配置
2. 确保 `config.py` 中的默认值也是正确的
3. 使用环境变量覆盖默认值

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

### 认证功能检查
- [x] 用户注册流程正常
- [x] 用户登录流程正常
- [x] JWT令牌生成正常
- [x] 访客模式访问正常
- [x] 路由权限控制正常

## 💡 经验总结

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

## 🔧 常用命令速查

```bash
# 虚拟环境管理
backend\.venv\Scripts\activate          # 激活虚拟环境
deactivate                              # 退出虚拟环境

# 依赖管理
pip install -r backend/requirements.txt # 安装依赖
pip list | findstr package_name         # 查看包版本

# 服务启动
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload  # 启动后端
cd frontend
npm run dev               # 启动前端（端口3000）

# 数据库管理
python backend/init_auth_tables.py      # 初始化认证表
python backend/check_database.py        # 检查数据库结构
mysql -u weatheruser -p                 # 连接数据库

# 认证测试
# 前端访问: http://localhost:3000/login
# 后端API: http://127.0.0.1:8000/docs

# 缓存清理
Remove-Item -Path "__pycache__" -Recurse -Force  # 清理Python缓存
```

## ✉️ 邮件推送天气（2025-08-19）

> 本节说明新加入的"邮件推送天气（立即/定时）"功能、技术实现、使用说明、数据库变更与常见问题。

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
  - 如需手工迁移（已在代码中使用）：
    ```sql
    ALTER TABLE email_schedules ADD COLUMN IF NOT EXISTS city_name VARCHAR(100) NULL;
    ALTER TABLE email_schedules ADD COLUMN IF NOT EXISTS province  VARCHAR(100) NULL;
    ```

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

### 调度器与资源占用
- 轮询周期：默认 60 秒（可调）
- 每次处理：最多 20 条（可调）
- 失败回退：5 分钟后再试
- 说明：扫描查询为轻量 SQL，批量小、发送串行，开销可控；如需更高性能可按需开启并发发送或缩短轮询间隔

### 配置项（后端）
- 调度器（`app/main.py`）
  - `EmailScheduleWorker(AsyncSessionLocal, interval_seconds=60, batch_size=20)`
- 发送限流（`notification_service.py`）
  - `MIN_INTERVAL_SECONDS`：最小间隔秒数（针对 user+email）
  - `DAILY_QUOTA`：每日配额
  - `RATE_LIMIT_ENABLED`：限流总开关（开发/联调可关闭）

### 常见问题 & 解决方案
- 启动时报 ORM 关系错误（删除 `city_id` 后）
  - 方案：`City.favorites` 改为名称+省份的 `primaryjoin`（`viewonly=True`），不再依赖外键
- 立即发送 422/500
  - 原因：前端传 `city_id` 或后端未解析 ID
  - 方案：统一使用 `city_name + province`，后端 `search_city(query)` 解析和风 `location id`
- 频繁限制误判（429）
  - 方案：只统计 `SENT` 记录；判定维度为 `(user_id, email)`；支持总开关 `RATE_LIMIT_ENABLED`
- 定时报 500：`Unknown column 'city_name' in 'field list'`
  - 方案：补齐 `email_schedules.city_name/province` 两列（见上文 SQL）
- 收藏点击后天气页面空白/Invalid Date
  - 方案：点击收藏时用"省份+城市名"重新搜索获取带 `id` 的城市对象，再拉取天气

## 🤖 RAG 智能穿衣建议（2025-08-21）

> 本节说明基于 RAG (Retrieval-Augmented Generation) + Gemini AI 实现的智能穿衣建议功能，为用户提供个性化的穿搭推荐。

### 功能概览
- **AI穿衣建议**
  - 基于实时天气数据（温度、湿度、风力、天气状况）生成个性化穿搭建议
  - 集成在邮件预览/发送功能中，自动附加在天气信息后
  - 支持不同天气条件的专业穿搭指导（晴天、雨天、大风等）
  - 考虑温差变化，提供全天候穿衣方案

### 技术架构

#### **RAG 检索增强生成**
```
用户请求 → 天气数据提取 → 语义查询构建 → 向量检索 → LLM生成 → 穿衣建议
```

#### **技术栈**
- **向量数据库**: Pinecone（云端托管，毫秒级检索）
- **嵌入模型**: BAAI/bge-base-zh-v1.5（768维中文语义向量）
- **生成模型**: Google Gemini 1.5 Flash（快速响应，成本优化）
- **知识库**: 专业时尚穿搭知识（Excel→向量化存储）

#### **关键组件**
- `rag_service.py`: RAG核心服务（检索+生成）
- `notification_service.py`: 邮件服务集成RAG
- `ingest_pinecone.py`: 知识库向量化脚本
- `knowledge_base.xlsx`: 穿搭知识库（可编辑）

### 实现流程

#### **1. 天气数据组织**
```python
weather_info = {
    "city_name": "广州",
    "condition": "多云",        # 天气状况
    "temp": "28",             # 当前温度
    "feels_like": "30",       # 体感温度
    "humidity": "75",         # 湿度
    "wind_dir": "东南风",      # 风向
    "wind_scale": "2",        # 风力等级
    "temp_max": "32",         # 今日最高温
    "temp_min": "26"          # 今日最低温
}
```

#### **2. 语义查询构建**
```python
def build_query_from_weather(info):
    parts = []
    if info.get("condition"):
        parts.append(f"天气{info['condition']}")
    if info.get("feels_like"):
        parts.append(f"体感温度{info['feels_like']}度")
    if info.get("humidity"):
        parts.append(f"湿度{info['humidity']}%")
    return "，".join(parts)  # "天气多云，体感温度30度，湿度75%"
```

#### **3. 向量检索匹配**
```python
def retrieve_rag_context(query, top_k=4):
    embedder = _get_embedder()  # bge-base-zh-v1.5
    index = _get_index()        # Pinecone索引
    vec = embedder.encode(query, normalize_embeddings=True).tolist()
    res = index.query(vector=vec, top_k=top_k, include_metadata=True)
    return "\n".join([m["metadata"]["text"] for m in res["matches"]])
```

#### **4. Gemini 生成建议**
```python
def generate_advice(weather_info, rag_context):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    你是专业穿搭顾问。基于以下知识库与天气信息，生成穿衣建议：
    
    [知识库参考]
    {rag_context}
    
    [天气信息]
    城市：{weather_info['city_name']}
    当前温度：{weather_info['temp']}°C
    体感温度：{weather_info['feels_like']}°C
    ...
    
    [要求]
    - 4条要点，每条不超过40字
    - 考虑温差变化和特殊天气
    - 语气专业温和
    """
    return model.generate_content(prompt).text
```

### 集成与调用

#### **邮件预览集成**
邮件预览/发送时自动调用RAG服务：


#### **独立API接口**
```python
# routers/rag.py
@router.get("/fashion-advice")
async def fashion_advice(city_id: str, city_name: str):
    # 完整的RAG流程，返回详细信息
    return {
        "weather": weather_info,
        "query": query,
        "rag_context": rag_context,
        "advice": advice
    }
```

### 前端体验优化

#### **超时与降级**
- **全局超时**: 30秒 (axios)
- **通知接口**: 45秒 (RAG+生成耗时)
- **降级策略**: RAG失败时返回基础天气信息

#### **用户交互**
- 每个收藏城市卡片都有独立的"✉️"按钮
- 点击后弹窗自动选中对应城市
- 预览区显示完整的"天气+穿衣建议"
- 生成过程中显示"生成预览中…"状态

### 知识库管理

#### **Excel 格式**
```
| id | category | suggestion |
|----|----------|------------|
| 1  | 高温     | 选择轻薄透气的棉质T恤，避免深色衣物... |
| 2  | 降雨     | 准备防水外套和雨伞，选择快干材质... |
```

#### **向量化入库**
```bash
# 执行向量化脚本
python backend/rag/ingest_pinecone.py

# 输出示例
正在初始化Pinecone...
正在加载Embedding模型...
读取知识库文件: knowledge_base.xlsx
正在生成向量...
准备上传 150 条向量到Pinecone...
数据入库完成！
```

### 环境配置

#### **必需环境变量**
```bash
# .env 文件
PINECONE_API_KEY=your_pinecone_key
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-flash  # 可选，默认flash
```

#### **依赖安装**
```bash
# 后端新增依赖
pip install sentence-transformers pinecone-client google-generativeai
```

### 性能与成本

#### **响应时间**
- **向量检索**: <100ms (Pinecone)
- **语义编码**: 200-500ms (本地模型)
- **文本生成**: 1-3秒 (Gemini Flash)
- **总耗时**: 通常2-5秒

#### **成本优化**
- **模型选择**: Gemini 1.5 Flash (成本是Pro的1/20)
- **检索缓存**: 相同查询复用结果
- **降级机制**: AI失败时仍有基础功能

### 扩展方向

#### **知识库增强**
- [ ] 季节性穿搭知识
- [ ] 不同职业场景穿搭
- [ ] 地域文化差异考虑
- [ ] 用户个人偏好学习

#### **功能扩展**
- [ ] 穿搭图片推荐
- [ ] 服装搭配色彩建议
- [ ] 购物清单生成
- [ ] 历史穿搭记录

---

> 如需把调度频率/发送并发进一步参数化或增加"任务列表/取消任务"接口，可在 `routers/notifications.py` 与 `services/scheduler.py` 基础上扩展。

```
