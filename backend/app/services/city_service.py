from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional, List

from app.database.models.city import City
from app.database.models.user_favorite import UserFavorite


class CityService:
    async def get_city_by_name(self, db: AsyncSession, city_name: str, province: str = None) -> Optional[City]:
        """根据城市名和省份获取城市信息"""
        query = select(City).where(City.city_name == city_name)
        if province:
            query = query.where(City.province == province)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_city(self, db: AsyncSession, city_name: str, province: str, 
                         country: str = "中国", latitude: float = None, longitude: float = None) -> City:
        """创建新城市"""
        city = City(
            city_name=city_name,
            province=province,
            country=country,
            latitude=latitude,
            longitude=longitude,
            search_count=1,
            last_searched_at=datetime.utcnow()
        )
        db.add(city)
        await db.commit()
        await db.refresh(city)
        return city
    
    async def increment_search_count(self, db: AsyncSession, city_name: str, province: str = None) -> bool:
        """增加城市搜索次数"""
        city = await self.get_city_by_name(db, city_name, province)
        if city:
            city.search_count += 1
            city.last_searched_at = datetime.utcnow()
            await db.commit()
            return True
        return False
    
    async def get_or_create_city(self, db: AsyncSession, city_name: str, province: str, 
                                country: str = "中国", latitude: float = None, longitude: float = None) -> City:
        """获取或创建城市"""
        city = await self.get_city_by_name(db, city_name, province)
        if not city:
            city = await self.create_city(db, city_name, province, country, latitude, longitude)
        else:
            await self.increment_search_count(db, city_name, province)
            # 重新获取更新后的城市信息
            city = await self.get_city_by_name(db, city_name, province)
        
        return city
    
    async def get_user_favorites(self, db: AsyncSession, user_id: int) -> List[UserFavorite]:
        """获取用户收藏的城市"""
        result = await db.execute(
            select(UserFavorite).where(UserFavorite.user_id == user_id)
        )
        return result.scalars().all()
    
    async def add_user_favorite(self, db: AsyncSession, user_id: int, city_name: str, 
                               province: str) -> UserFavorite:
        """添加用户收藏"""
        # 检查是否已经收藏
        existing = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.city_name == city_name,
                UserFavorite.province == province
            )
        )
        
        if existing.scalar_one_or_none():
            raise ValueError("该城市已在收藏列表中")
        
        favorite = UserFavorite(
            user_id=user_id,
            city_name=city_name,
            province=province
        )
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return favorite
    
    async def remove_user_favorite(self, db: AsyncSession, user_id: int, city_name: str, 
                                  province: str) -> bool:
        """移除用户收藏"""
        result = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.city_name == city_name,
                UserFavorite.province == province
            )
        )
        
        favorite = result.scalar_one_or_none()
        if favorite:
            await db.delete(favorite)
            await db.commit()
            return True
        return False
    
    async def get_popular_cities(self, db: AsyncSession, limit: int = 10) -> List[City]:
        """获取热门城市"""
        result = await db.execute(
            select(City)
            .order_by(City.search_count.desc())
            .limit(limit)
        )
        return result.scalars().all()


city_service = CityService()
