from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel
from datetime import datetime, timedelta
import secrets

class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    verification_code = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    verification_expires_at = Column(DateTime, nullable=True)
    
    # 关联关系
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 生成6位随机验证码
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        # 设置验证码过期时间（10分钟）
        if not self.verification_expires_at:
            self.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    @staticmethod
    def generate_verification_code() -> str:
        """生成6位数字验证码"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def is_verification_expired(self) -> bool:
        """检查验证码是否过期"""
        if not self.verification_expires_at:
            return True
        return datetime.utcnow() > self.verification_expires_at
    
    def refresh_verification_code(self):
        """刷新验证码"""
        self.verification_code = self.generate_verification_code()
        self.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
        self.is_verified = False
    
    def verify_code(self, code: str) -> bool:
        """验证验证码"""
        if self.is_verification_expired():
            return False
        if self.verification_code == code:
            self.is_verified = True
            self.verification_code = None
            self.verification_expires_at = None
            return True
        return False
    
    def to_dict(self):
        """转换为字典，排除敏感信息"""
        data = super().to_dict()
        # 排除敏感字段
        sensitive_fields = ['password_hash', 'verification_code']
        for field in sensitive_fields:
            data.pop(field, None)
        return data
