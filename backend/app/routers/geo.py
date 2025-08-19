from fastapi import APIRouter, Query
from app.services import qweather
from typing import List, Dict, Any

router = APIRouter(prefix="", tags=["geo"])

@router.get("/geo")
async def geo_lookup(query: str = Query(min_length=1, description="城市名，如：北京")):
    """城市搜索API - 直接使用和风天气原生API"""
    return await qweather.search_city(query)


