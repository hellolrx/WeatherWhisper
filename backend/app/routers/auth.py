from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.database.connection import get_db
from app.database.models.user import User
from app.database.models.email_verification import EmailVerification
from app.services.email_service import email_service
from app.core.config import settings
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserVerifyRequest,
    UserVerifyResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserProfileResponse
)

# 创建路由
router = APIRouter(prefix="/auth", tags=["用户认证"])

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# 工具函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), 
                          db: AsyncSession = Depends(get_db)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

# 路由端点
@router.post("/register/email", response_model=UserRegisterResponse)
async def send_verification_email(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送注册验证码"""
    try:
        # 检查邮箱是否已存在
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )
            else:
                # 如果用户存在但未验证，刷新验证码
                existing_user.refresh_verification_code()
                await db.commit()
                user = existing_user
        else:
            # 创建新用户（临时，未验证）
            user = User(
                email=request.email,
                username=request.username,
                password_hash="",  # 临时密码哈希
                verification_code=User.generate_verification_code()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # 发送验证码邮件
        email_sent = await email_service.send_verification_email(
            to_email=request.email,
            verification_code=user.verification_code,
            username=request.username
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="验证码发送失败，请稍后重试"
            )
        
        return UserRegisterResponse(
            message="验证码已发送到您的邮箱",
            email=request.email,
            expires_in_minutes=10
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/register/verify", response_model=UserVerifyResponse)
async def verify_email_code(
    request: UserVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """验证邮箱验证码"""
    try:
        # 查找用户
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证验证码
        if user.verify_code(request.verification_code):
            await db.commit()
            return UserVerifyResponse(
                message="邮箱验证成功",
                email=request.email,
                is_verified=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证失败: {str(e)}"
        )

@router.post("/register/complete", response_model=UserProfileResponse)
async def complete_registration(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """完成注册（设置密码）"""
    try:
        # 查找已验证的用户
        result = await db.execute(
            select(User).where(User.email == email, User.is_verified == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在或未验证"
            )
        
        # 设置密码
        user.password_hash = get_password_hash(password)
        await db.commit()
        await db.refresh(user)
        
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册完成失败: {str(e)}"
        )

@router.post("/login", response_model=UserLoginResponse)
async def user_login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    try:
        # 查找用户
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先验证邮箱"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户已被禁用"
            )
        
        # 验证密码
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=settings.access_token_expire_minutes,
            user=UserProfileResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                is_verified=user.is_verified,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """获取用户信息"""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
