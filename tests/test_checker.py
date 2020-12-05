import pytest
from pydantic import EmailError
from fastapi_mail.email_utils.errors import DBProvaiderError


@pytest.mark.asyncio
async def test_default_checker(default_checker):
    await default_checker.fetch_temp_email_domains()
    assert default_checker.TEMP_EMAIL_DOMAINS != []

    email = "tural_m@hotmail.com"
    domain = email.split("@")[-1]

    assert await default_checker.is_dispasoble(email) is False
    assert await default_checker.is_blocked_domain(domain) is False
    assert await default_checker.is_blocked_address(email) is False
    assert await default_checker.check_mx_record(domain) is True

    with pytest.raises(NotImplementedError):
        default_checker.catch_all_check()

    await default_checker.add_temp_domain([domain])

    assert await default_checker.is_dispasoble(email) is True
    assert await default_checker.is_blocked_domain(domain) is False
    assert await default_checker.is_blocked_address(email) is False
    assert await default_checker.check_mx_record(domain) is True

    await default_checker.blacklist_add_domain(domain)

    assert await default_checker.is_blocked_domain(domain) is True
    assert await default_checker.is_blocked_address(email) is False
    assert await default_checker.check_mx_record(domain) is True

    await default_checker.blacklist_add_email(email)

    assert await default_checker.is_blocked_address(email) is True
    assert await default_checker.check_mx_record(domain) is True

    assert default_checker.validate_email(email) is True

    with pytest.raises(EmailError):
        default_checker.validate_email("test#mail.com")

    with pytest.raises(DBProvaiderError):
        await default_checker.close_connections()
