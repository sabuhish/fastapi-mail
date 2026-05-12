import pytest

from fastapi_mail.email_utils import DefaultChecker


@pytest.mark.asyncio
async def test_redis_checker(redis_checker):
    redis_checker.TEMP_EMAIL_DOMAINS = []
    redis_checker.BLOCKED_ADDRESSES = {}
    redis_checker.BLOCKED_DOMAINS = {}
    email = "test_me@hotmail.com"
    domain = email.split("@")[-1]

    assert await redis_checker.is_disposable(email) is False
    assert await redis_checker.is_blocked_domain(domain) is False
    assert await redis_checker.is_blocked_address(email) is False
    assert await redis_checker.check_mx_record(domain) is True

    await redis_checker.add_temp_domain([domain])

    assert await redis_checker.is_disposable(email) is True
    assert await redis_checker.is_blocked_domain(domain) is False
    assert await redis_checker.is_blocked_address(email) is False
    assert await redis_checker.check_mx_record(domain) is True

    await redis_checker.blacklist_add_domain(domain)

    assert await redis_checker.is_blocked_domain(domain) is True
    assert await redis_checker.is_blocked_address(email) is False
    assert await redis_checker.check_mx_record(domain) is True

    await redis_checker.blacklist_add_email(email)

    assert await redis_checker.is_blocked_address(email) is True
    assert await redis_checker.check_mx_record(domain) is True


class FakeRedisClient:
    async def get(self, key):
        return 1

    async def hgetall(self, key):
        return {"existing": 1}


async def temp_domains():
    return ["example.com"]


@pytest.mark.asyncio
async def test_default_redis_connection_uses_localhost_fallback(monkeypatch):
    urls = []

    async def from_url(url, **kwargs):
        urls.append(url)
        return FakeRedisClient()

    checker = DefaultChecker(db_provider="redis")
    monkeypatch.setattr(
        "fastapi_mail.email_utils.email_check.aioredis.from_url", from_url
    )
    monkeypatch.setattr(checker, "fetch_temp_email_domains", temp_domains)

    await checker.init_redis()

    assert urls == ["redis://localhost:6379/0"]


@pytest.mark.asyncio
async def test_custom_redis_host_overrides_localhost_fallback(monkeypatch):
    urls = []

    async def from_url(url, **kwargs):
        urls.append(url)
        return FakeRedisClient()

    checker = DefaultChecker(db_provider="redis", redis_host="redis")
    monkeypatch.setattr(
        "fastapi_mail.email_utils.email_check.aioredis.from_url", from_url
    )
    monkeypatch.setattr(checker, "fetch_temp_email_domains", temp_domains)

    await checker.init_redis()

    assert urls == ["redis://redis:6379/0"]


@pytest.mark.asyncio
async def test_existing_redis_client_does_not_create_new_connection(
    monkeypatch, redis_checker
):
    async def from_url(url, **kwargs):
        raise AssertionError("from_url should not be called for an existing client")

    monkeypatch.setattr(
        "fastapi_mail.email_utils.email_check.aioredis.from_url", from_url
    )
    monkeypatch.setattr(redis_checker, "fetch_temp_email_domains", temp_domains)

    await redis_checker.init_redis()
