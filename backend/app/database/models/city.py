from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.orm import relationship, foreign
from app.database.models.base import BaseModel
from datetime import datetime

class City(BaseModel):
    """城市模型"""
    
    __tablename__ = "cities"
    
    city_name = Column(String(100), nullable=False, index=True)
    province = Column(String(100), nullable=True, index=True)
    country = Column(String(100), default="中国", nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    search_count = Column(Integer, default=1, nullable=False)
    last_searched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系（按名称+省份映射，非外键）
    favorites = relationship(
        "UserFavorite",
        primaryjoin="and_(foreign(UserFavorite.city_name)==City.city_name, foreign(UserFavorite.province)==City.province)",
        back_populates="city",
        viewonly=True
    )
    weather_caches = relationship("WeatherCache", back_populates="city", cascade="all, delete-orphan")
    
    def increment_search_count(self):
        """增加搜索次数"""
        self.search_count += 1
        self.last_searched_at = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        # 转换Decimal类型为float
        if data.get('latitude'):
            data['latitude'] = float(data['latitude'])
        if data.get('longitude'):
            data['longitude'] = float(data['longitude'])
        return data
    
    @classmethod
    def create_or_update(cls, session, city_data: dict):
        """创建或更新城市记录"""
        city_name = city_data.get('city_name')
        province = city_data.get('province')
        
        # 查找现有城市
        existing_city = session.query(cls).filter(
            cls.city_name == city_name,
            cls.province == province
        ).first()
        
        if existing_city:
            # 更新现有记录
            existing_city.increment_search_count()
            # 更新坐标信息（如果提供了新的）
            if city_data.get('latitude'):
                existing_city.latitude = city_data['latitude']
            if city_data.get('longitude'):
                existing_city.longitude = city_data['longitude']
            return existing_city
        else:
            # 创建新记录
            new_city = cls(**city_data)
            session.add(new_city)
            return new_city
