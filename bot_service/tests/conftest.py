import pytest
from fakeredis.aioredis import FakeRedis


@pytest.fixture
async def fake_redis():
    client = FakeRedis(decode_responses=True)
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


@pytest.fixture(autouse=True)
def patch_redis_in_handlers(monkeypatch, fake_redis):
    monkeypatch.setattr("app.bot.handlers.get_redis", lambda: fake_redis)
