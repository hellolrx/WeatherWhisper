from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal


class SendWeatherEmailRequest(BaseModel):
    city_id: Optional[str] = Field(default=None, description="和风天气城市ID（可选）")
    city_name: Optional[str] = Field(default=None, description="城市名称（可选，与province一起提供）")
    province: Optional[str] = Field(default=None, description="省份（可选，与city_name一起提供）")
    email: Optional[EmailStr] = Field(None, description="收件邮箱，不填则使用当前用户邮箱")
    dry_run: bool = Field(default=False, description="仅预览，不真正发送")


class SendWeatherEmailResponse(BaseModel):
    message: str
    preview: str
    quota_remaining: int


class ScheduleType(BaseModel):
    type: Literal['ONCE', 'DAILY']


class ScheduleWeatherEmailRequest(BaseModel):
    city_id: Optional[str] = Field(default=None)
    city_name: Optional[str] = Field(default=None)
    province: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = None
    type: Literal['ONCE', 'DAILY'] = Field(default='DAILY')
    time: str = Field(default='09:00', description="HH:mm，Asia/Shanghai")
    date: Optional[str] = Field(default=None, description="YYYY-MM-DD，type=ONCE时必填")
    timezone: str = Field(default='Asia/Shanghai')


class ScheduleWeatherEmailResponse(BaseModel):
    schedule_id: int
    next_run_at: str
    message: str 