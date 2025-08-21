import os
from typing import Any, Dict, Optional, List
from pathlib import Path

import httpx
from cachetools import TTLCache
from fastapi import HTTPException, status
from dotenv import load_dotenv


# 明确从 backend/.env 加载环境变量，避免启动目录不同找不到 .env
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
# 初始加载一次，下面的函数每次请求会再次加载覆盖
load_dotenv(dotenv_path=ENV_PATH, override=True)

def _get_hosts() -> tuple[str, str]:
	# 每次请求前刷新环境变量，支持运行时修改 .env
	load_dotenv(dotenv_path=ENV_PATH, override=True)
	base = os.getenv("QWEATHER_BASE", "https://devapi.qweather.com")
	geo = os.getenv("QWEATHER_GEO", "https://geoapi.qweather.com")
	return base, geo

_cache: TTLCache[str, Any] = TTLCache(maxsize=1024, ttl=60)


def _ensure_api_key() -> str:
	load_dotenv(dotenv_path=ENV_PATH, override=True)
	api_key = os.getenv("QWEATHER_API_KEY")
	if not api_key:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
			"code": "QWEATHER_API_KEY_MISSING",
			"message": "QWEATHER_API_KEY 未设置，请在 backend/.env 中配置"
		})
	return api_key


def _cache_key(url: str, params: Dict[str, Any]) -> str:
	# 生成稳定的 key
	key = url + "?" + "&".join(f"{k}={params[k]}" for k in sorted(params.keys()))
	return key


async def _get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
	api_key = _ensure_api_key()
	params_with_key = {**params, "key": api_key}

	key = _cache_key(url, params_with_key)
	if key in _cache:
		return _cache[key]

	retry = 0
	last_exc: Exception | None = None
	while retry < 2:  # 简单重试 1 次
		async with httpx.AsyncClient(timeout=12.0) as client:
			try:
				resp = await client.get(url, params=params_with_key)
				resp.raise_for_status()
				data = resp.json()
				_cache[key] = data
				return data
			except httpx.HTTPStatusError as exc:
				last_exc = exc
				break  # 状态码错误不重试
			except httpx.HTTPError as exc:
				last_exc = exc
				retry += 1
				continue

	# 失败时抛出更明确的异常
	if isinstance(last_exc, httpx.HTTPStatusError):
		raise HTTPException(status_code=last_exc.response.status_code, detail={
			"code": "QWEATHER_HTTP_ERROR",
			"message": f"请求和风天气失败: {last_exc.response.text}",
		})
	else:
		raise HTTPException(status_code=502, detail={
			"code": "QWEATHER_NETWORK_ERROR",
			"message": f"网络错误: {str(last_exc) if last_exc else '未知错误'}",
		})


async def search_city(query: str) -> Dict[str, Any]:
	"""城市搜索API - 和风天气原生支持层级搜索"""
	_, geo = _get_hosts()
	url = f"{geo}/v2/city/lookup"
	return await _get_json(url, {"location": query})


async def weather_now(location: str) -> Dict[str, Any]:
	"""获取实时天气"""
	base, _ = _get_hosts()
	url = f"{base}/v7/weather/now"
	return await _get_json(url, {"location": location})


async def weather_24h(location: str) -> Dict[str, Any]:
	"""获取24小时天气预报"""
	base, _ = _get_hosts()
	url = f"{base}/v7/weather/24h"
	return await _get_json(url, {"location": location})


async def weather_7d(location: str) -> Dict[str, Any]:
	"""获取7天天气预报"""
	base, _ = _get_hosts()
	url = f"{base}/v7/weather/7d"
	return await _get_json(url, {"location": location})


async def weather_3d(location: str) -> Dict[str, Any]:
	"""获取3天天气预报（用于获取当日最高/最低气温）"""
	base, _ = _get_hosts()
	url = f"{base}/v7/weather/3d"
	return await _get_json(url, {"location": location})


