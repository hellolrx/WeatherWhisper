from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 登录尝试限制配置
MAX_LOGIN_ATTEMPTS = 10
LOCKOUT_DURATION = timedelta(minutes=30)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    # 刷新令牌有效期30天
    expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None

def create_password_reset_token() -> str:
    """创建密码重置令牌"""
    return secrets.token_urlsafe(32)

def check_login_attempts(email: str, recent_attempts: list) -> tuple[bool, Optional[datetime], int]:
    """
    检查登录尝试次数
    
    Returns:
        tuple: (是否被锁定, 锁定到期时间, 剩余尝试次数)
    """
    if not recent_attempts:
        return False, None, MAX_LOGIN_ATTEMPTS
    
    # 统计最近的失败尝试
    recent_failures = [
        attempt for attempt in recent_attempts 
        if not attempt.success and 
        attempt.attempt_time > datetime.utcnow() - timedelta(minutes=30)
    ]
    
    if len(recent_failures) >= MAX_LOGIN_ATTEMPTS:
        # 计算锁定到期时间
        latest_attempt = max(attempt.attempt_time for attempt in recent_failures)
        lockout_until = latest_attempt + LOCKOUT_DURATION
        
        if datetime.utcnow() < lockout_until:
            return True, lockout_until, 0
        else:
            # 锁定时间已过，重置计数
            return False, None, MAX_LOGIN_ATTEMPTS
    
    remaining = MAX_LOGIN_ATTEMPTS - len(recent_failures)
    return False, None, remaining

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return str(secrets.randbelow(1000000)).zfill(6)

def is_token_expired(token_data: dict) -> bool:
    """检查令牌是否过期"""
    if "exp" not in token_data:
        return True
    
    exp_timestamp = token_data["exp"]
    if isinstance(exp_timestamp, (int, float)):
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
    else:
        exp_datetime = exp_timestamp
    
    return datetime.utcnow() > exp_datetime 