from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


def _get_allowed_origins() -> list[str]:
    allow_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [o.strip() for o in allow_origins.split(",") if o.strip()]


app = FastAPI(title="WeatherWhisper API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers.geo import router as geo_router  # noqa: E402
from app.routers.weather import router as weather_router  # noqa: E402
from app.services import qweather  # noqa: E402


app.include_router(geo_router, prefix="/api")
app.include_router(weather_router, prefix="/api")


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


