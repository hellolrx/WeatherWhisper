from sqlalchemy import Column, String, Boolean, DateTime, Enum
from app.database.models.base import BaseModel
from datetime import datetime, timedelta

class EmailVerification(BaseModel):
    """邮箱验证记录模型"""
    
    __tablename__ = "email_verifications"
    
    email = Column(String(100), nullable=False, index=True)
    verification_code = Column(String(6), nullable=False)
    verification_type = Column(Enum('register', 'reset_password', name='verification_type_enum'), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    def is_expired(self) -> bool:
        """检查验证码是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """检查验证码是否有效（未使用且未过期）"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """标记验证码为已使用"""
        self.is_used = True
    
    @classmethod
    def create_verification(cls, email: str, verification_code: str, 
                          verification_type: str, ttl_minutes: int = 10):
        """创建验证记录"""
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        return cls(
            email=email,
            verification_code=verification_code,
            verification_type=verification_type,
            expires_at=expires_at
        )
