import os
import json
import uuid
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

_client = None

def get_redis():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


def save_report(report: dict) -> str:
    r = get_redis()
    report_id = uuid.uuid4().hex[:10]  # e.g. "a3f9c12b4e"
    r.setex(f"report:{report_id}", TTL_SECONDS, json.dumps(report))
    return report_id


def load_report(report_id: str) -> dict | None:
    r = get_redis()
    data = r.get(f"report:{report_id}")
    if data is None:
        return None
    return json.loads(data)