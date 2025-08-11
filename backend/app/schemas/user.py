from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """用户创建模型"""
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    email: str
    username: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 