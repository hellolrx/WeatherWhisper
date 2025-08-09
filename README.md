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
```
WeatherWhisper/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   │   ├── geo.py     # 城市查询
│   │   │   └── weather.py # 天气接口
│   │   ├── services/
│   │   │   └── qweather.py # 和风天气对接与缓存
│   │   └── main.py        # 应用入口
│   ├── .env               # API密钥配置（本地）
│   └── requirements.txt   # Python 依赖
└── frontend/              # Vue3 前端
    ├── src/
    │   ├── views/
    │   │   └── Dashboard.vue # 主页面
    │   ├── stores/
    │   │   └── favorites.ts  # 收藏管理
    │   ├── utils/
    │   │   └── http.ts      # Axios 封装
    │   ├── router/
    │   └── App.vue
    ├── vite.config.ts     # Vite 配置（含代理）
    └── package.json       # Node 依赖

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

## 许可说明
- 本项目仅用于学习交流
- 请遵守和风天气开发者协议
- 图标版权归和风天气所有