from fastapi import APIRouter, HTTPException, Query
from app.services import qweather
from app.services.rag_service import build_query_from_weather, retrieve_rag_context, generate_advice

router = APIRouter(prefix="", tags=["RAG"])


@router.get("/fashion-advice")
async def fashion_advice(city_id: str = Query(..., description="和风城市ID"), city_name: str = Query(..., description="城市名称")):
	# 1) 拉取天气数据
	try:
		now = await qweather.weather_now(city_id)
		d3 = await qweather.weather_3d(city_id)
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"天气服务异常: {e}")

	# 2) 组织结构化天气信息
	now_data = now.get("now", {}) if isinstance(now, dict) else {}
	first_day = (d3.get("daily", [{}])[0]) if isinstance(d3, dict) else {}
	weather_info = {
		"city_name": city_name,
		"obs_time": (now_data.get("obsTime", "").replace("T", " ").replace("+08:00", "")),
		"condition": now_data.get("text"),
		"temp": now_data.get("temp"),
		"feels_like": now_data.get("feelsLike"),
		"wind_dir": now_data.get("windDir"),
		"wind_scale": now_data.get("windScale"),
		"humidity": now_data.get("humidity"),
		"temp_max": first_day.get("tempMax"),
		"temp_min": first_day.get("tempMin"),
	}

	# 3) RAG 检索
	query = build_query_from_weather(weather_info)
	rag_ctx = retrieve_rag_context(query, top_k=4)

	# 4) LLM 生成
	try:
		advice = generate_advice(weather_info, rag_ctx)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"生成建议失败: {e}")

	return {
		"weather": weather_info,
		"query": query,
		"rag_context": rag_ctx,
		"advice": advice,
	} 