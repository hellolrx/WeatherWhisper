from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import get_db
from app.schemas.notifications import (
    SendWeatherEmailRequest, SendWeatherEmailResponse,
    ScheduleWeatherEmailRequest, ScheduleWeatherEmailResponse
)
from app.services.notification_service import notification_service
from app.services.user_service import user_service
from app.database.models import UserFavorite, EmailSchedule
from app.services import qweather

router = APIRouter(prefix="/notifications", tags=["邮件通知"])
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    payload = user_service.verify_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证")
    return int(payload.get("sub"))


async def resolve_city(db: AsyncSession, user_id: int, req_city_id: str | None, city_name: str | None, province: str | None, require_favorite: bool = True):
    if req_city_id:
        # 兼容旧参数：若有city_id则直接返回一个轻量对象
        class _Obj: ...
        o = _Obj(); o.city_id = req_city_id; o.city_name = city_name or ""; o.province = province or ""; return o
    # 无 city_id，则按名称匹配收藏
    if city_name:
        q = select(UserFavorite).where(UserFavorite.user_id == user_id, UserFavorite.city_name == city_name)
        if province:
            q = q.where(UserFavorite.province == province)
        result = await db.execute(q)
        fav = result.scalar_one_or_none()
        if not fav:
            if require_favorite:
                raise HTTPException(status_code=400, detail="请先收藏该城市或提供有效的city_id")
            else:
                class _Obj: ...
                o = _Obj(); o.city_name = city_name; o.province = province or ""; return o
        return fav
    raise HTTPException(status_code=422, detail="缺少城市参数")


async def get_qweather_id(city_name: str, province: str | None) -> str:
    # 调用和风城市查询，尽量精确匹配 省份+城市
    query = f"{province or ''} {city_name}".strip()
    data = await qweather.search_city(query)
    locs = data.get("location", []) if isinstance(data, dict) else []
    if not locs:
        raise HTTPException(status_code=404, detail="未找到城市的和风ID")
    # 优先精确匹配
    for x in locs:
        if x.get("name") == city_name and ((province is None) or x.get("adm1") == province):
            return x.get("id")
    return locs[0].get("id")


@router.post("/send-weather", response_model=SendWeatherEmailResponse)
async def send_weather_email(
    req: SendWeatherEmailRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    # 默认邮箱
    email = req.email
    if not email:
        from app.database.models.user import User
        u = await db.get(User, user_id)
        email = u.email if u else None
    if not email:
        raise HTTPException(status_code=400, detail="无法确定收件邮箱")

    fav = await resolve_city(db, user_id, req.city_id, req.city_name, req.province, require_favorite=not req.dry_run)
    city_name = getattr(fav, "city_name", req.city_name)
    province = getattr(fav, "province", req.province)
    if not city_name:
        raise HTTPException(status_code=422, detail="缺少城市名称")

    # 解析和风ID（预览与发送都需要）
    location_id = await get_qweather_id(city_name, province)

    if req.dry_run:
        preview = await notification_service.preview(location_id, city_name)
        quota = await notification_service._check_quota(db, user_id)
        return SendWeatherEmailResponse(message="预览成功", preview=preview, quota_remaining=quota)

    ok, preview, left = await notification_service.send_now(db, user_id, email, location_id, city_name)
    if not ok:
        raise HTTPException(status_code=429, detail=preview)
    return SendWeatherEmailResponse(message="发送成功", preview=preview, quota_remaining=left)


@router.post("/schedule-weather", response_model=ScheduleWeatherEmailResponse)
async def schedule_weather_email(
    req: ScheduleWeatherEmailRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    if not req.type:
        req.type = 'DAILY'
    # 默认邮箱
    if not req.email:
        from app.database.models.user import User
        u = await db.get(User, user_id)
        req.email = u.email if u else None
    if not req.email:
        raise HTTPException(status_code=400, detail="无法确定收件邮箱")

    fav = await resolve_city(db, user_id, req.city_id, req.city_name, req.province, require_favorite=True)
    city_name = getattr(fav, "city_name", req.city_name)
    province = getattr(fav, "province", req.province)
    if not city_name:
        raise HTTPException(status_code=422, detail="缺少城市名称")

    location_id = await get_qweather_id(city_name, province)

    next_run = notification_service.next_run_for(req.type, req.time, req.date, req.timezone)
    from datetime import timezone
    utc_next_run = next_run.astimezone(timezone.utc)

    schedule = EmailSchedule(
        user_id=user_id,
        email=req.email,
        city_id=location_id,
        city_name=city_name,
        province=province,
        type=req.type,
        time_hhmm=req.time,
        date=req.date,
        timezone=req.timezone,
        next_run_at=utc_next_run
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return ScheduleWeatherEmailResponse(schedule_id=schedule.id, next_run_at=next_run.isoformat(), message="定时创建成功") 