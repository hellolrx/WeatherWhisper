import os
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import google.generativeai as genai


# 懒加载与单例资源
_model: SentenceTransformer | None = None
_pc: Pinecone | None = None
_index = None

INDEX_NAME = "fashion-advice"


def _ensure_env():
	load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)


def _get_embedder() -> SentenceTransformer:
	global _model
	if _model is None:
		_ensure_env()
		_model = SentenceTransformer('BAAI/bge-base-zh-v1.5')
	return _model


def _get_index():
	global _pc, _index
	if _index is None:
		_ensure_env()
		api_key = os.getenv("PINECONE_API_KEY")
		if not api_key:
			raise RuntimeError("PINECONE_API_KEY 未配置")
		_pc = Pinecone(api_key=api_key)
		if INDEX_NAME not in _pc.list_indexes().names():
			raise RuntimeError(f"Pinecone 索引不存在: {INDEX_NAME}")
		_index = _pc.Index(INDEX_NAME)
	return _index


def _get_gemini():
	_ensure_env()
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("GEMINI_API_KEY 未配置")
	genai.configure(api_key=api_key)
	model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
	return genai.GenerativeModel(model_name)


def build_query_from_weather(info: Dict[str, Any]) -> str:
	parts = []
	if info.get("condition"):
		parts.append(f"天气{info['condition']}")
	if info.get("feels_like"):
		parts.append(f"体感温度{info['feels_like']}度")
	if info.get("humidity"):
		parts.append(f"湿度{info['humidity']}%")
	if info.get("wind_dir") and info.get("wind_scale"):
		parts.append(f"{info['wind_dir']}{info['wind_scale']}级")
	return "，".join(parts) or "穿衣建议"


def retrieve_rag_context(query: str, top_k: int = 4) -> str:
	embedder = _get_embedder()
	index = _get_index()
	vec = embedder.encode(query, normalize_embeddings=True).tolist()
	res = index.query(vector=vec, top_k=top_k, include_metadata=True)
	items = []
	for m in res.get("matches", []):
		md = m.get("metadata") or {}
		text = md.get("text")
		if text:
			items.append(text)
	return "\n".join(items)


def generate_advice(weather_info: Dict[str, Any], rag_context: str) -> str:
	model = _get_gemini()
	prompt = f"""
你是一名专业的穿搭顾问。请基于以下 RAG 知识库内容与实时天气信息，为用户生成今日穿衣建议。

[RAG参考]
{rag_context}

[天气信息]
城市：{weather_info.get('city_name')}
当前时间：{weather_info.get('obs_time')}
天气状况：{weather_info.get('condition')}
当前温度：{weather_info.get('temp')}°C
体感温度：{weather_info.get('feels_like')}°C
风向/风力：{weather_info.get('wind_dir')} {weather_info.get('wind_scale')}级
湿度：{weather_info.get('humidity')}%
今日最高/最低：{weather_info.get('temp_max')}°C / {weather_info.get('temp_min')}°C

[要求]
- 输出 4 条要点，每条不超过 40 字，务必可执行
- 若有降雨或大风，增加防护与材质建议
- 先给整体风格定位，再给关键单品
- 语气温和专业，避免夸张词
""".strip()
	resp = model.generate_content(prompt)
	return resp.text if hasattr(resp, 'text') else str(resp) 