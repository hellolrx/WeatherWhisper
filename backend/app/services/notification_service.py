from datetime import datetime, timedelta, timezone
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import EmailNotification, EmailSchedule, UserFavorite
from app.services.qweather import weather_now, weather_7d
from app.services.email_service import email_service


DAILY_QUOTA = 50
MIN_INTERVAL_SECONDS = 2
RATE_LIMIT_ENABLED = False  # 频率/配额限制开关（临时关闭）
TZ_SH = timezone(timedelta(hours=8))  # Asia/Shanghai 等效


class NotificationService:
	async def _check_quota(self, db: AsyncSession, user_id: int) -> int:
		start_of_day = datetime.now(TZ_SH).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
		result = await db.execute(
			select(func.count(EmailNotification.id)).where(
				EmailNotification.user_id == user_id,
				EmailNotification.status == "SENT",
				EmailNotification.created_at >= start_of_day
			)
		)
		count = result.scalar_one()
		return max(0, DAILY_QUOTA - count)
	
	async def _check_interval(self, db: AsyncSession, user_id: int, email: str) -> bool:
		threshold = datetime.utcnow() - timedelta(seconds=MIN_INTERVAL_SECONDS)
		result = await db.execute(
			select(func.max(EmailNotification.created_at)).where(
				EmailNotification.user_id == user_id,
				EmailNotification.email == email,
				EmailNotification.status == "SENT"
			)
		)
		last = result.scalar_one_or_none()
		return not last or last <= threshold
	
	def _compose_text(self, city_name: str, now_data: dict, today_data: dict | None) -> str:
		now = now_data.get("now", {})
		obs = now.get("obsTime", "").replace("T", " ").replace("+08:00", "")
		text = now.get("text", "")
		temp = now.get("temp", "")
		feels = now.get("feelsLike", "")
		wind_dir = now.get("windDir", "")
		wind_scale = now.get("windScale", "")
		hum = now.get("humidity", "")
		max_t, min_t = "", ""
		if today_data:
			try:
				max_t = today_data["daily"][0]["tempMax"]
				min_t = today_data["daily"][0]["tempMin"]
			except Exception:
				pass
		return (
			f"现在是 {obs}，{city_name} {text}。当前 {temp}°C，体感 {feels}°C，{wind_dir}{wind_scale}级，湿度 {hum}%"
			+ (f"；今日最高 {max_t}°C、最低 {min_t}°C" if max_t and min_t else "")
			+ "。\n（出门建议：后续接入 LLM 生成）"
		)
	
	async def preview(self, city_id: str, city_name: str) -> str:
		now = await weather_now(city_id)
		d7 = await weather_7d(city_id)
		return self._compose_text(city_name, now, d7)
	
	async def send_now(self, db: AsyncSession, user_id: int, email: str, city_id: str, city_name: str) -> Tuple[bool, str, int]:
		# 配额与频率检查（可关闭）
		if RATE_LIMIT_ENABLED:
			quota = await self._check_quota(db, user_id)
			if quota <= 0:
				return False, "今日配额已用尽（50/50）", 0
			if not await self._check_interval(db, user_id, email):
				return False, f"操作过于频繁，请稍后再试（{MIN_INTERVAL_SECONDS}秒后）", quota
		else:
			quota = DAILY_QUOTA
		text = await self.preview(city_id, city_name)
		subject = f"天语 · 今日天气｜{city_name}"
		ok = await email_service.send_plain_email(email, subject, text)
		rec = EmailNotification(
			user_id=user_id, email=email, city_id=city_id,
			subject=subject, content=text,
			status="SENT" if ok else "FAILED",
			error_message=None if ok else "SMTP发送失败"
		)
		db.add(rec)
		await db.commit()
		left = max(0, quota - 1) if ok else quota
		return ok, text, left
	
	def next_run_for(self, type_: str, time_hhmm: str, date: str | None, tz: str) -> datetime:
		now = datetime.now(TZ_SH)
		hour, minute = map(int, time_hhmm.split(":"))
		if type_ == "ONCE":
			if date:
				y, m, d = map(int, date.split("-"))
				candidate = datetime(y, m, d, hour, minute, tzinfo=TZ_SH)
			else:
				candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
			if candidate <= now:
				candidate = candidate + timedelta(days=1)
			return candidate
		else:
			candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
			if candidate <= now:
				candidate = candidate + timedelta(days=1)
			return candidate

notification_service = NotificationService() 