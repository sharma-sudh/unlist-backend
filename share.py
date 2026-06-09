import os
import json
import uuid
import hashlib
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REPORT_TTL = 7 * 24 * 60 * 60    # 7 days
CACHE_TTL = 30 * 24 * 60 * 60    # 30 days

_client = None

def get_redis():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


def save_report(report: dict) -> str:
    r = get_redis()
    report_id = uuid.uuid4().hex[:10]
    r.setex(f"report:{report_id}", REPORT_TTL, json.dumps(report))
    return report_id


def load_report(report_id: str) -> dict | None:
    r = get_redis()
    data = r.get(f"report:{report_id}")
    return json.loads(data) if data else None


def get_cached_analyse(url: str) -> dict | None:
    r = get_redis()
    key = f"analyse:{hashlib.md5(url.encode()).hexdigest()}"
    data = r.get(key)
    return json.loads(data) if data else None


def cache_analyse(url: str, result: dict):
    r = get_redis()
    key = f"analyse:{hashlib.md5(url.encode()).hexdigest()}"
    r.setex(key, CACHE_TTL, json.dumps(result))