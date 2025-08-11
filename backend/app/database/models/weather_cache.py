from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel
from datetime import datetime, timedelta
import json

class WeatherCache(BaseModel):
    """天气数据缓存模型"""
    
    __tablename__ = "weather_cache"
    
    city_name = Column(String(100), nullable=False, index=True)
    province = Column(String(100), nullable=True)
    weather_type = Column(Enum('now', '24h', '7d', name='weather_type_enum'), nullable=False)
    weather_data = Column(Text, nullable=False)  # JSON格式存储
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # 关联关系
    city = relationship("City", back_populates="weather_caches")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果weather_data是dict，转换为JSON字符串
        if isinstance(self.weather_data, dict):
            self.weather_data = json.dumps(self.weather_data, ensure_ascii=False)
    
    def get_weather_data(self):
        """获取天气数据（JSON反序列化）"""
        try:
            return json.loads(self.weather_data) if self.weather_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_weather_data(self, data: dict):
        """设置天气数据（自动序列化为JSON）"""
        self.weather_data = json.dumps(data, ensure_ascii=False)
    
    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        # 反序列化天气数据
        data['weather_data'] = self.get_weather_data()
        return data
    
    @classmethod
    def create_cache(cls, city_name: str, province: str, weather_type: str, 
                    weather_data: dict, ttl_minutes: int = 60):
        """创建缓存记录"""
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        return cls(
            city_name=city_name,
            province=province,
            weather_type=weather_type,
            weather_data=weather_data,
            expires_at=expires_at
        )
