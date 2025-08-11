# WeatherWhisper (天语)

一个基于 Vue3 + FastAPI 的本地天气应用，对接和风天气 API，支持城市搜索、多天气类型展示与本地收藏。

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
│   │   │   └── weather.py # 天气数据接口
│   │   ├── services/
│   │   │   └── qweather.py # 第三方API服务层
│   │   └── main.py        # 应用入口
│   ├── .env               # 环境变量配置
│   └── requirements.txt   # Python 依赖
└── frontend/              # Vue3 前端（模块化重构）
    ├── src/
    │   ├── components/     # 🧩 组件库
    │   │   ├── search/     # 搜索相关组件
    │   │   │   └── SearchBox.vue
    │   │   ├── favorites/  # 收藏功能组件
    │   │   │   └── FavoriteCities.vue
    │   │   └── weather/    # 天气显示组件
    │   │       ├── CurrentWeather.vue
    │   │       ├── HourlyForecast.vue
    │   │       └── DailyForecast.vue
    │   ├── composables/    # 🎣 组合式API
    │   │   ├── useWeatherApi.ts    # 天气API服务
    │   │   └── useGeolocation.ts   # 地理位置服务
    │   ├── stores/         # 📦 状态管理
    │   │   └── favorites.ts # 收藏城市Store
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

```

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

### 前端启动检查
- [x] Node.js环境正常
- [x] 依赖包安装完成
- [x] 开发服务器启动成功
- [x] 端口5173监听正常
- [x] 代理配置正确

### 数据库配置检查
- [x] MySQL服务运行正常
- [x] 数据库用户权限正确
- [x] 数据库表结构完整
- [x] 连接字符串格式正确

## 💡 经验总结

1. **环境隔离很重要**：使用虚拟环境避免系统包冲突
2. **配置文件要同步**：代码默认值和环境变量要保持一致
3. **依赖版本要兼容**：注意包之间的版本兼容性
4. **错误信息要仔细看**：很多问题都有明确的错误提示
5. **分步骤解决问题**：一次解决一个问题，避免同时修改多个地方

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
npm run dev                                    # 启动前端

# 数据库管理
python backend/init_database.py         # 初始化数据库
mysql -u weatheruser -p                 # 连接数据库

# 缓存清理
Remove-Item -Path "__pycache__" -Recurse -Force  # 清理Python缓存
```
