from pydantic import BaseModel
from typing import Optional

class CityCreate(BaseModel):
    """城市创建模型"""
    name: str
    location_id: str
    country: str
    adm1: str
    adm2: str

class CityResponse(BaseModel):
    """城市响应模型"""
    id: int
    name: str
    location_id: str
    country: str
    adm1: str
    adm2: str
    is_favorite: bool = False

    class Config:
        from_attributes = True

class CitySearchRequest(BaseModel):
    """城市搜索请求模型"""
    query: str 