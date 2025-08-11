from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.database.models.user import User
from app.database.models.email_verification import EmailVerification
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, email: str, username: str, password: str) -> User:
        """创建用户"""
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            password_hash=hashed_password,
            is_verified=True,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def update_user_verification(self, db: AsyncSession, email: str, verification_code: str) -> bool:
        """更新用户验证状态"""
        result = await db.execute(
            update(User)
            .where(User.email == email)
            .values(
                is_verified=True,
                verification_code=None,
                verification_expires_at=None
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def create_email_verification(self, db: AsyncSession, email: str, code: str, 
                                      verification_type: str = "registration") -> EmailVerification:
        """创建邮箱验证记录"""
        verification = EmailVerification(
            email=email,
            code=code,
            verification_type=verification_type,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.add(verification)
        await db.commit()
        await db.refresh(verification)
        return verification
    
    async def verify_email_code(self, db: AsyncSession, email: str, code: str, 
                               verification_type: str = "registration") -> bool:
        """验证邮箱验证码"""
        result = await db.execute(
            select(EmailVerification)
            .where(
                EmailVerification.email == email,
                EmailVerification.code == code,
                EmailVerification.verification_type == verification_type,
                EmailVerification.is_used == False,
                EmailVerification.expires_at > datetime.utcnow()
            )
        )
        verification = result.scalar_one_or_none()
        
        if verification:
            # 标记为已使用
            verification.is_used = True
            await db.commit()
            return True
        
        return False


user_service = UserService()
