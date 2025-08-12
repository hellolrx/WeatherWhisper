from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "WeatherWhisper"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 数据库配置 - 默认密码设置为admin123
    database_url: str = os.getenv("DATABASE_URL", "mysql+asyncmy://root:admin123@localhost:3306/weatherwhisper")
    
    # QQ邮箱SMTP配置
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.qq.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "lrx8389@qq.com")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # 和风天气API配置
    qweather_api_key: str = os.getenv("QWEATHER_API_KEY", "")
    qweather_geo: str = os.getenv("QWEATHER_GEO", "https://geoapi.qweather.com")
    qweather_base: str = os.getenv("QWEATHER_BASE", "https://devapi.qweather.com")
    
    # 安全配置
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    
    # CORS配置 - 从环境变量解析逗号分隔的字符串
    @property
    def allow_origins(self) -> List[str]:
        origins_str = os.getenv("ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        # 禁用环境变量自动解析，避免JSON解析错误
        env_parse_none_str = None
        # 允许额外字段，避免配置冲突
        extra = "allow"

# 创建全局设置实例
settings = Settings()
