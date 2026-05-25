"""분석 결과 캐시(gpt:*) 일괄 삭제. VT 캐시는 보존."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from upstash_redis import Redis

load_dotenv(Path(__file__).parent.parent.parent / ".env")

redis = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"],
)

cursor = 0
deleted = 0
while True:
    cursor, keys = redis.scan(cursor=cursor, match="gpt:*", count=100)
    if keys:
        redis.delete(*keys)
        deleted += len(keys)
    if cursor == 0:
        break

print(f"삭제됨: {deleted}개 gpt:* 키")
sys.exit(0)
