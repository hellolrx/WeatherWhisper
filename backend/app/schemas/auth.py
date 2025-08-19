from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """用户基础信息"""
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度必须至少8位')
        return v

class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str
    remember_me: bool = False

class UserResponse(UserBase):
    """用户信息响应"""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

class LoginAttemptResponse(BaseModel):
    """登录尝试响应"""
    success: bool
    message: str
    remaining_attempts: Optional[int] = None
    locked_until: Optional[datetime] = None
    user: Optional[UserResponse] = None
    tokens: Optional[TokenResponse] = None

class SendVerificationRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr
    verification_type: str = Field(..., pattern="^(register|reset_password)$")

class VerifyCodeRequest(BaseModel):
    """验证验证码请求"""
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    verification_type: str = Field(..., pattern="^(register|reset_password)$")

class RegisterWithVerificationRequest(BaseModel):
    """带验证码的用户注册请求"""
    user_data: UserCreate
    verification_code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
