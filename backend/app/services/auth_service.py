from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.database.models.user import User
from app.database.models.user_favorite import UserFavorite
from app.database.models.email_verification import EmailVerification
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, create_password_reset_token, check_login_attempts
)
from app.core.config import settings
from app.services.email_service import email_service
import random
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """认证服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def send_verification_code(self, email: str, verification_type: str = "register") -> Tuple[bool, str]:
        """
        发送验证码到指定邮箱
        
        Args:
            email: 邮箱地址
            verification_type: 验证类型 (register, reset_password)
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查邮箱是否已注册（注册时）
            if verification_type == "register":
                existing_user = await self._get_user_by_email(email)
                if existing_user:
                    return False, "该邮箱已被注册"
            
            # 生成6位数字验证码
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # 检查是否已有未过期的验证码
            existing_verification = await self._get_valid_verification(email, verification_type)
            if existing_verification:
                # 更新现有验证码
                existing_verification.verification_code = verification_code
                existing_verification.expires_at = datetime.utcnow() + timedelta(minutes=10)
                existing_verification.is_used = False
            else:
                # 创建新的验证记录
                new_verification = EmailVerification.create_verification(
                    email=email,
                    verification_code=verification_code,
                    verification_type=verification_type,
                    ttl_minutes=10
                )
                self.db.add(new_verification)
            
            await self.db.commit()
            
            # 发送验证码邮件
            if verification_type == "register":
                success = await email_service.send_verification_email(email, verification_code)
            else:
                success = await email_service.send_password_reset_email(email, verification_code)
            
            if success:
                logger.info(f"验证码发送成功: {email}")
                return True, "验证码已发送到您的邮箱，请注意查收"
            else:
                return False, "验证码发送失败，请稍后重试"
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"发送验证码失败: {e}")
            return False, "发送验证码失败，请稍后重试"
    
    async def verify_email_code(self, email: str, verification_code: str, verification_type: str = "register") -> Tuple[bool, str]:
        """
        验证邮箱验证码
        
        Args:
            email: 邮箱地址
            verification_code: 验证码
            verification_type: 验证类型
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 查找验证记录
            verification = await self._get_valid_verification(email, verification_type)
            if not verification:
                return False, "验证码不存在或已过期"
            
            # 检查验证码是否匹配
            if verification.verification_code != verification_code:
                return False, "验证码错误"
            
            # 标记验证码为已使用
            verification.mark_as_used()
            await self.db.commit()
            
            logger.info(f"邮箱验证成功: {email}")
            return True, "邮箱验证成功"
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"验证邮箱验证码失败: {e}")
            return False, "验证失败，请稍后重试"
    
    async def register_user(self, user_data: UserCreate, verification_code: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册（需要邮箱验证）
        
        Args:
            user_data: 用户注册数据
            verification_code: 邮箱验证码
            
        Returns:
            Tuple[bool, str, Optional[User]]: (是否成功, 消息, 用户对象)
        """
        try:
            # 验证邮箱验证码
            is_valid, message = await self.verify_email_code(user_data.email, verification_code, "register")
            if not is_valid:
                return False, message, None
            
            # 检查邮箱是否已存在
            existing_user = await self._get_user_by_email(user_data.email)
            if existing_user:
                return False, "邮箱已被注册", None
            
            # 检查用户名是否已存在
            existing_username = await self._get_user_by_username(user_data.username)
            if existing_username:
                return False, "用户名已被使用", None
            
            # 创建新用户
            hashed_password = get_password_hash(user_data.password)
            new_user = User(
                email=user_data.email,
                username=user_data.username,
                password_hash=hashed_password,
                verification_code="",  # 注册成功后清空验证码字段
                is_active=True,
                is_verified=True,  # 邮箱已验证
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            
            logger.info(f"新用户注册成功: {user_data.email}")
            return True, "注册成功", new_user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"用户注册失败: {e}")
            return False, "注册失败，请稍后重试", None

    async def authenticate_user(self, user_data: UserLogin, ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[User], Optional[TokenResponse]]:
        """
        用户认证
        
        Returns:
            Tuple[bool, str, Optional[User], Optional[TokenResponse]]: (是否成功, 消息, 用户对象, 令牌)
        """
        try:
            # 查找用户
            user = await self._get_user_by_email(user_data.email)
            if not user:
                return False, "邮箱不存在", None, None
            
            if not user.is_active:
                return False, "账户已被禁用", None, None
            
            # 验证密码
            if not verify_password(user_data.password, user.password_hash):
                return False, "密码错误", None, None
            
            # 检查是否已验证
            if not user.is_verified:
                return False, "请先验证邮箱", None, None
            
            # 登录成功
            logger.info(f"用户登录成功: {user_data.email}")
            
            # 生成令牌
            tokens = await self._create_user_tokens(user, user_data.remember_me)
            
            return True, "登录成功", user, tokens
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return False, "登录失败，请稍后重试", None, None
    
    async def refresh_tokens(self, refresh_token: str) -> Tuple[bool, str, Optional[TokenResponse]]:
        """
        刷新访问令牌
        """
        try:
            # 验证刷新令牌
            from app.core.security import verify_token
            payload = verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return False, "无效的刷新令牌", None
            
            # 获取用户
            user_id = payload.get("sub")
            if not user_id:
                return False, "令牌格式错误", None
            
            user = await self._get_user_by_id(user_id)
            if not user or not user.is_active:
                return False, "用户不存在或已被禁用", None
            
            # 生成新令牌
            tokens = await self._create_user_tokens(user, remember_me=True)
            
            return True, "令牌刷新成功", tokens
            
        except Exception as e:
            logger.error(f"令牌刷新失败: {e}")
            return False, "令牌刷新失败", None
    
    async def get_user_profile(self, user_id: int) -> Optional[User]:
        """获取用户资料"""
        return await self._get_user_by_id(user_id)
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_valid_verification(self, email: str, verification_type: str) -> Optional[EmailVerification]:
        """获取有效的验证记录"""
        result = await self.db.execute(
            select(EmailVerification).where(
                and_(
                    EmailVerification.email == email,
                    EmailVerification.verification_type == verification_type,
                    EmailVerification.is_used == False,
                    EmailVerification.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def _create_user_tokens(self, user: User, remember_me: bool = False) -> TokenResponse:
        """创建用户令牌"""
        # 访问令牌有效期：记住我7天，否则30分钟
        if remember_me:
            access_expires = timedelta(days=7)
        else:
            access_expires = timedelta(minutes=30)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_expires.total_seconds())
        ) 