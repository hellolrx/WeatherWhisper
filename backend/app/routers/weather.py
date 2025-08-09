from fastapi import APIRouter, Query
from app.services import qweather


router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/now")
async def get_now(location: str = Query(min_length=1, description="和风城市ID")):
    return await qweather.weather_now(location)


@router.get("/24h")
async def get_24h(location: str = Query(min_length=1, description="和风城市ID")):
    return await qweather.weather_24h(location)


@router.get("/7d")
async def get_7d(location: str = Query(min_length=1, description="和风城市ID")):
    return await qweather.weather_7d(location)


