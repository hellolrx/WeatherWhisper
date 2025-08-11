from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

from app.database.models.weather_cache import WeatherCache


class WeatherCacheService:
    async def get_cached_weather(self, db: AsyncSession, city_name: str, 
                                province: str, weather_type: str) -> Optional[Dict[str, Any]]:
        """获取缓存的天气数据"""
        result = await db.execute(
            select(WeatherCache).where(
                WeatherCache.city_name == city_name,
                WeatherCache.province == province,
                WeatherCache.weather_type == weather_type,
                WeatherCache.expires_at > datetime.utcnow()
            )
        )
        
        cache = result.scalar_one_or_none()
        if cache:
            return cache.weather_data
        return None
    
    async def set_cached_weather(self, db: AsyncSession, city_name: str, province: str, 
                                weather_type: str, weather_data: Dict[str, Any], 
                                expires_in_minutes: int = 30) -> WeatherCache:
        """设置天气数据缓存"""
        # 删除旧的缓存
        await db.execute(
            delete(WeatherCache).where(
                WeatherCache.city_name == city_name,
                WeatherCache.province == province,
                WeatherCache.weather_type == weather_type
            )
        )
        
        # 创建新缓存
        cache = WeatherCache(
            city_name=city_name,
            province=province,
            weather_type=weather_type,
            weather_data=weather_data,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        )
        
        db.add(cache)
        await db.commit()
        await db.refresh(cache)
        return cache
    
    async def clear_expired_cache(self, db: AsyncSession) -> int:
        """清理过期的缓存"""
        result = await db.execute(
            delete(WeatherCache).where(WeatherCache.expires_at <= datetime.utcnow())
        )
        await db.commit()
        return result.rowcount
    
    async def get_cache_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """获取缓存统计信息"""
        # 总缓存数量
        total_result = await db.execute(select(WeatherCache))
        total_count = len(total_result.scalars().all())
        
        # 过期缓存数量
        expired_result = await db.execute(
            select(WeatherCache).where(WeatherCache.expires_at <= datetime.utcnow())
        )
        expired_count = len(expired_result.scalars().all())
        
        # 有效缓存数量
        valid_count = total_count - expired_count
        
        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "expired_count": expired_count
        }
    
    async def clear_all_cache(self, db: AsyncSession) -> int:
        """清理所有缓存"""
        result = await db.execute(delete(WeatherCache))
        await db.commit()
        return result.rowcount


weather_cache_service = WeatherCacheService()
