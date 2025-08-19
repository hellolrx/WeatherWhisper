from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    RefreshTokenRequest, LoginAttemptResponse, SendVerificationRequest,
    VerifyCodeRequest, RegisterWithVerificationRequest
)
from app.core.security import verify_token
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()

# 依赖函数：获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserResponse]:
    """获取当前认证用户"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌格式错误"
            )
        
        auth_service = AuthService(db)
        user = await auth_service.get_user_profile(int(user_id))
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败"
        )

@router.post("/send-verification", response_model=dict, status_code=status.HTTP_200_OK)
async def send_verification_code(
    request: SendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送邮箱验证码"""
    try:
        auth_service = AuthService(db)
        success, message = await auth_service.send_verification_code(
            request.email, 
            request.verification_type
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "success": True,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送验证码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送验证码失败，请稍后重试"
        )

@router.post("/verify-code", response_model=dict, status_code=status.HTTP_200_OK)
async def verify_email_code(
    request: VerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """验证邮箱验证码"""
    try:
        auth_service = AuthService(db)
        success, message = await auth_service.verify_email_code(
            request.email,
            request.verification_code,
            request.verification_type
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "success": True,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证验证码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证失败，请稍后重试"
        )

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: RegisterWithVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册（需要邮箱验证）"""
    try:
        auth_service = AuthService(db)
        success, message, user = await auth_service.register_user(
            user_data.user_data, 
            user_data.verification_code
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "success": True,
            "message": message,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )

@router.post("/login", response_model=LoginAttemptResponse)
async def login_user(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    try:
        # 获取客户端信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        auth_service = AuthService(db)
        success, message, user, tokens = await auth_service.authenticate_user(
            user_data, ip_address, user_agent
        )
        
        if success:
            return LoginAttemptResponse(
                success=True,
                message=message,
                user=UserResponse.from_orm(user),
                tokens=tokens
            )
        else:
            # 简化版本，不记录登录尝试次数
            return LoginAttemptResponse(
                success=False,
                message=message,
                remaining_attempts=None
            )
            
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        auth_service = AuthService(db)
        success, message, tokens = await auth_service.refresh_tokens(refresh_data.refresh_token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败"
        )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户资料"""
    return current_user

@router.post("/logout", response_model=dict)
async def logout_user(
    current_user: UserResponse = Depends(get_current_user)
):
    """用户登出"""
    # 注意：JWT是无状态的，真正的登出需要在客户端删除令牌
    # 这里可以记录登出日志或实现令牌黑名单
    return {
        "success": True,
        "message": "登出成功"
    }

@router.get("/guest", response_model=dict)
async def guest_mode():
    """访客模式信息"""
    return {
        "success": True,
        "message": "访客模式已启用",
        "features": {
            "weather_search": True,
            "weather_display": True,
            "favorites": False,
            "user_profile": False
        }
    }
