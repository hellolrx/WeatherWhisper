from fastapi import APIRouter, Query
from app.services import qweather


router = APIRouter(prefix="", tags=["geo"])


@router.get("/geo")
async def geo_lookup(query: str = Query(min_length=1, description="城市名，如：北京")):
    return await qweather.search_city(query)


