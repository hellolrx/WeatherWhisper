from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WeatherCacheCreate(BaseModel):
    """天气缓存创建模型"""
    location_id: str
    weather_data: dict
    cache_type: str  # 'now', '24h', '7d'
    expires_at: datetime

class WeatherCacheResponse(BaseModel):
    """天气缓存响应模型"""
    id: int
    location_id: str
    weather_data: dict
    cache_type: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True 