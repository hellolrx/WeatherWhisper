from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime, timedelta

class User(Base):
    """用户表 - 匹配现有数据库结构"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    verification_code = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    
    # 关联关系
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )

class LoginAttempt(Base):
    """登录尝试记录表"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可以为空，用于记录未知用户的尝试
    email = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6最长45字符
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=False)
    attempt_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="login_attempts")
    
    # 索引
    __table_args__ = (
        Index('idx_login_attempt_email_time', 'email', 'attempt_time'),
        Index('idx_login_attempt_user_time', 'user_id', 'attempt_time'),
    )

class UserFavorite(Base):
    """用户收藏城市表"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city_id = Column(String(50), nullable=False)  # 和风天气城市ID
    city_name = Column(String(100), nullable=False)
    adm1 = Column(String(100), nullable=True)  # 省份
    adm2 = Column(String(100), nullable=True)  # 市级行政区
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="favorites")
    
    # 索引
    __table_args__ = (
        Index('idx_user_favorite_user_city', 'user_id', 'city_id'),
        Index('idx_user_favorite_city', 'city_id'),
    )

class PasswordResetToken(Base):
    """密码重置令牌表"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_password_reset_token', 'token'),
        Index('idx_password_reset_user', 'user_id'),
    ) 