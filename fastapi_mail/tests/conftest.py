import os
import pytest
import fakeredis.aioredis
from pytest_mock import mock

from fastapi_mail.email_utils import DefaultChecker
from fastapi_mail.config import ConnectionConfig


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


@pytest.fixture(autouse=True)
def mail_config():
    env = {
        "MAIL_USERNAME": "example@test.com",
        "MAIL_PASSWORD": "strong password",
        "MAIL_FROM": "example@test.com",
        "MAIL_PORT": "587",
        "MAIL_SERVER": "smtp.gmail.com",
        "MAIL_TLS": "True",
        "MAIL_SSL": "False",
        "SUPPRESS_SEND": "1"
    }

    yield env
