import pytest
import fakeredis.aioredis
from fastapi_mail.email_utils import DefaultChecker

@pytest.fixture
def default_checker():
    test = DefaultChecker()
    yield test
    del test


@pytest.fixture
@pytest.mark.asyncio
async def redis_checker(scope="redis_config"):
    test = DefaultChecker(db_provider="redis")
    test.redis_client = await  fakeredis.aioredis.create_redis_pool(encoding="UTF-8")
    await test.init_redis()
    yield test
    await test.redis_client.flushall()
    await test.close_connections()