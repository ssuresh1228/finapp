import redis.asyncio as aioredis

async def test_redis():
    try:
        redis_client = aioredis.from_url("redis://localhost:6379")
        await redis_client.set("test", "value")
        value = await redis_client.get("test")
        print(f"Redis test value: {value}")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")