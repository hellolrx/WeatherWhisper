from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager


def _get_allowed_origins() -> list[str]:
    allow_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [o.strip() for o in allow_origins.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    from app.database.connection import init_db, close_db, AsyncSessionLocal
    from app.services.scheduler import EmailScheduleWorker

    try:
        await init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
    
    # 启动定时任务调度器（每60秒扫描一次）
    worker = EmailScheduleWorker(AsyncSessionLocal, interval_seconds=60, batch_size=20)
    worker.start()
    print("🕒 定时任务调度器已启动")

    try:
        yield
    finally:
        # 关闭调度器与数据库连接
        try:
            await worker.stop()
            print("🛑 定时任务调度器已停止")
        except Exception:
            pass
        await close_db()


app = FastAPI(
    title="WeatherWhisper API", 
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers.geo import router as geo_router  # noqa: E402
from app.routers.weather import router as weather_router  # noqa: E402
from app.routers.auth import router as auth_router  # noqa: E402
from app.routers.favorites import router as favorites_router  # noqa: E402
from app.routers.notifications import router as notifications_router  # noqa: E402
from app.services import qweather  # noqa: E402


app.include_router(geo_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    # 不返回密钥，仅返回配置状态与当前 Host 以便排障
    try:
        _ = qweather._ensure_api_key()
        has_key = True
    except Exception:
        has_key = False
    base, geo = qweather._get_hosts()
    return {"status": "ok", "hasApiKey": has_key, "hosts": {"base": base, "geo": geo}}


