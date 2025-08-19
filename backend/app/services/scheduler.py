import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.database.models import EmailSchedule
from app.services.notification_service import notification_service


class EmailScheduleWorker:
	"""简易邮件定时任务调度器：每60秒扫描到期任务并发送邮件。
	资源控制：
	- 每次最多处理 batch_size 条（默认20）
	- 失败回退5分钟后重试
	- 对 DAILY 任务，发送成功后 next_run_at += 1 day
	"""
	def __init__(self, session_factory: async_sessionmaker[AsyncSession], interval_seconds: int = 60, batch_size: int = 20):
		self._session_factory = session_factory
		self._interval = interval_seconds
		self._batch_size = batch_size
		self._running = False
		self._task: Optional[asyncio.Task] = None

	async def _tick(self):
		utc_now = datetime.now(timezone.utc)
		async with self._session_factory() as db:
			result = await db.execute(
				select(EmailSchedule)
				.where(
					EmailSchedule.status == "ACTIVE",
					EmailSchedule.next_run_at <= utc_now
				)
				.order_by(EmailSchedule.next_run_at)
				.limit(self._batch_size)
			)
			schedules: List[EmailSchedule] = result.scalars().all()
			if not schedules:
				return
			for sch in schedules:
				try:
					ok, preview, _ = await notification_service.send_now(
						db,
						sch.user_id,
						sch.email,
						sch.city_id,
						sch.city_name or ""
					)
					sch.last_run_at = utc_now
					if sch.type == "DAILY":
						# 每日任务，设定下一次执行时间（+1 天）
						sch.next_run_at = (sch.next_run_at or utc_now) + timedelta(days=1)
					else:
						# 一次性任务：若成功则置 SENT；失败则5分钟后重试
						if ok:
							sch.status = "SENT"
						else:
							sch.next_run_at = utc_now + timedelta(minutes=5)
					await db.commit()
				except Exception:
					# 出错时回退并推迟5分钟重试，避免阻塞
					await db.rollback()
					try:
						sch.next_run_at = utc_now + timedelta(minutes=5)
						await db.commit()
					except Exception:
						await db.rollback()

	async def _loop(self):
		self._running = True
		while self._running:
			try:
				await self._tick()
			except Exception:
				# 避免异常中断循环
				pass
			await asyncio.sleep(self._interval)

	def start(self):
		if self._task and not self._task.done():
			return
		self._task = asyncio.create_task(self._loop(), name="email-schedule-worker")

	async def stop(self):
		self._running = False
		if self._task:
			try:
				await asyncio.wait_for(self._task, timeout=self._interval + 5)
			except asyncio.TimeoutError:
				self._task.cancel() 