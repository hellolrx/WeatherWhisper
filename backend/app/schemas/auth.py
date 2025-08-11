from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=2, max_length=50, description="用户名")

class UserRegisterResponse(BaseModel):
    """用户注册响应"""
    message: str = Field(..., description="响应消息")
    email: str = Field(..., description="用户邮箱")
    expires_in_minutes: int = Field(..., description="验证码有效期（分钟）")

class UserVerifyRequest(BaseModel):
    """邮箱验证请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    verification_code: str = Field(..., min_length=6, max_length=6, description="6位验证码")

class UserVerifyResponse(BaseModel):
    """邮箱验证响应"""
    message: str = Field(..., description="响应消息")
    email: str = Field(..., description="用户邮箱")
    is_verified: bool = Field(..., description="是否验证成功")

class UserLoginRequest(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, description="用户密码")

class UserLoginResponse(BaseModel):
    """用户登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in_minutes: int = Field(..., description="令牌有效期（分钟）")
    user: "UserProfileResponse" = Field(..., description="用户信息")

class UserProfileResponse(BaseModel):
    """用户信息响应"""
    id: int = Field(..., description="用户ID")
    email: str = Field(..., description="用户邮箱")
    username: str = Field(..., description="用户名")
    is_verified: bool = Field(..., description="是否已验证")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
