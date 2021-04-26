import pytest


@pytest.mark.asyncio
async def test_redis_checker(redis_checker):
        
    redis_checker.TEMP_EMAIL_DOMAINS = []
    redis_checker.BLOCKED_ADDRESSES = {}
    redis_checker.BLOCKED_DOMAINS = {}
    email = "test_me@hotmail.com"
    domain = email.split("@")[-1]

    assert await redis_checker.is_dispasoble(email) is False
    assert await redis_checker.is_blocked_domain(domain) is False
    assert await redis_checker.is_blocked_address(email) is False
    assert await redis_checker.check_mx_record(domain) is True

    await redis_checker.add_temp_domain([domain])

    assert await redis_checker.is_dispasoble(email) is True
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
