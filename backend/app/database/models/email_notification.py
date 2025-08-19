from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel
from datetime import datetime


class EmailNotification(BaseModel):
	__tablename__ = "email_notifications"
	
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
	email = Column(String(255), nullable=False, index=True)
	city_id = Column(String(50), nullable=False)
	subject = Column(String(255), nullable=False)
	content = Column(Text, nullable=False)
	status = Column(String(20), default="SENT", nullable=False)  # SENT / FAILED
	error_message = Column(Text, nullable=True)
	
	user = relationship("User") 