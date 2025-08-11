from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel

class UserFavorite(BaseModel):
    """用户收藏城市模型"""
    
    __tablename__ = "user_favorites"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    city_name = Column(String(100), nullable=False, index=True)
    province = Column(String(100), nullable=True)
    
    # 关联关系
    user = relationship("User", back_populates="favorites")
    city = relationship("City", back_populates="favorites")
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        # 添加城市信息
        if self.city:
            data['city_info'] = self.city.to_dict()
        return data
