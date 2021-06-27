from pathlib import Path

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


@pytest.fixture(autouse=True)
def mail_config():
    home: Path = Path(__file__).parent.parent
    html = home / "files"
    env = {
        "MAIL_USERNAME": "example@test.com",
        "MAIL_PASSWORD":"strong",
        "MAIL_FROM": "example@test.com",
        "MAIL_FROM_NAME": "example",
        "MAIL_PORT": 25,
        "MAIL_SERVER": "localhost",
        "MAIL_TLS": False,
        "MAIL_SSL": False,
        "MAIL_DEBUG": 0,
        "SUPPRESS_SEND": 1,
        "USE_CREDENTIALS": False,
        "VALIDATE_CERTS": False,
        "TEMPLATE_FOLDER": html,
    }

    yield env
