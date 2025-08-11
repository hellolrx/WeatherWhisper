# 数据模型Schema模块
from .auth import *
from .user import *
from .city import *
from .weather import *

__all__ = [
    # Auth schemas
    "UserRegisterRequest",
    "UserRegisterResponse", 
    "UserVerifyRequest",
    "UserVerifyResponse",
    "UserLoginRequest",
    "UserLoginResponse",
    "UserProfileResponse",
    
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    
    # City schemas
    "CityCreate",
    "CityResponse",
    "CitySearchRequest",
    
    # Weather schemas
    "WeatherCacheCreate",
    "WeatherCacheResponse"
]
