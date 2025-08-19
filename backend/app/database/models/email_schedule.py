from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel


class EmailSchedule(BaseModel):
	__tablename__ = "email_schedules"
	
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
	email = Column(String(255), nullable=False)
	city_id = Column(String(50), nullable=False)
	city_name = Column(String(100), nullable=True)
	province = Column(String(100), nullable=True)
	type = Column(String(10), nullable=False, default="DAILY")  # ONCE / DAILY
	time_hhmm = Column(String(5), nullable=False, default="09:00")
	date = Column(String(10), nullable=True)  # YYYY-MM-DD for ONCE
	timezone = Column(String(64), nullable=False, default="Asia/Shanghai")
	next_run_at = Column(DateTime, nullable=False)
	status = Column(String(12), nullable=False, default="ACTIVE")  # ACTIVE / CANCELLED / SENT
	last_run_at = Column(DateTime, nullable=True)
	
	user = relationship("User") 