from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from jose import JWTError

from app.database.connection import get_db
from app.services.city_service import city_service
from app.services.user_service import user_service
from app.schemas.favorites import (
    FavoriteCityRequest,
    FavoriteCityResponse
)

router = APIRouter(prefix="/favorites", tags=["收藏城市"])


async def get_current_user(token: str = Depends(HTTPBearer()), db: AsyncSession = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = user_service.verify_token(token.credentials)
        if payload is None:
            raise credentials_exception
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return user_id


@router.post("/add", response_model=FavoriteCityResponse)
async def add_favorite_city(
    request: FavoriteCityRequest,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加收藏城市"""
    try:
        favorite = await city_service.add_user_favorite(
            db, current_user_id, request.city_name, request.province
        )
        
        # 确保城市信息存在（国家固定为中国，不再从入参传递）
        await city_service.get_or_create_city(
            db, request.city_name, request.province
        )
        
        return FavoriteCityResponse(
            id=favorite.id,
            city_name=favorite.city_name,
            province=favorite.province,
            created_at=favorite.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/remove/{city_name}")
async def remove_favorite_city(
    city_name: str,
    province: str,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """移除收藏城市"""
    success = await city_service.remove_user_favorite(db, current_user_id, city_name, province)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏的城市不存在")
    
    return {"message": "收藏已移除"}


@router.get("/list", response_model=List[FavoriteCityResponse])
async def get_favorite_cities(
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户收藏的城市列表"""
    favorites = await city_service.get_user_favorites(db, current_user_id)
    return [
        FavoriteCityResponse(
            id=fav.id,
            city_name=fav.city_name,
            province=fav.province,
            created_at=fav.created_at
        )
        for fav in favorites
    ]


@router.get("/popular", response_model=List[dict])
async def get_popular_cities(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取热门城市"""
    cities = await city_service.get_popular_cities(db, limit)
    return [
        {
            "city_name": city.city_name,
            "province": city.province,
            "country": city.country,
            "search_count": city.search_count,
            "last_searched_at": city.last_searched_at
        }
        for city in cities
    ]
