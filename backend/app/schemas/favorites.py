from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FavoriteCityRequest(BaseModel):
    city_name: str = Field(..., min_length=1, max_length=100, description="城市名称")
    province: str = Field(..., min_length=1, max_length=100, description="省份")
    country: str = Field(default="中国", min_length=1, max_length=100, description="国家")


class FavoriteCityResponse(BaseModel):
    id: int = Field(..., description="收藏ID")
    city_name: str = Field(..., description="城市名称")
    province: str = Field(..., description="省份")
    country: str = Field(..., description="国家")
    created_at: datetime = Field(..., description="收藏时间")
    
    class Config:
        from_attributes = True


class PopularCityResponse(BaseModel):
    city_name: str = Field(..., description="城市名称")
    province: str = Field(..., description="省份")
    country: str = Field(..., description="国家")
    search_count: int = Field(..., description="搜索次数")
    last_searched_at: datetime = Field(..., description="最后搜索时间")
    
    class Config:
        from_attributes = True
