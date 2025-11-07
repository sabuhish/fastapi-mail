import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Union

import dns.exception
import dns.resolver
from email_validator import EmailNotValidError, validate_email

try:
    from redis import asyncio as aioredis

    redis_lib = True
except ImportError:
    redis_lib = False

try:
    import httpx

    request_lib = True
except ImportError:
    request_lib = False

from fastapi_mail.errors import ApiError, DBProvaiderError


class AbstractEmailChecker(ABC):
    @abstractmethod
    def validate_email(self, email: str) -> bool:
        pass

    @abstractmethod
    async def is_disposable(self, email: str):
        pass

    @abstractmethod
    async def check_mx_record(self, domain: str, full_result: bool = False):
        pass

    @abstractmethod
    async def blacklist_add_email(self, email: str):
        pass

    @abstractmethod
    async def blacklist_add_domain(self, domain: str):
        pass

    @abstractmethod
    async def add_temp_domain(self, domain_lists: List[str]):
        pass

    @abstractmethod
    async def is_blocked_domain(self, domain: str):
        pass

    @abstractmethod
    async def is_blocked_address(self, email: str):
        pass

    @abstractmethod
    def catch_all_check(self):
        pass


class DefaultChecker(AbstractEmailChecker):
    """
    Default class for checking email from collected public resource.
    The class makes it possible to use redis to save data.

    :param source(optional): source for collected email data.
    :param db_provider: switch to redis
    :param redis_client(optional): existing async Redis client to reuse (recommended for apps with existing
                                    Redis connections)
    :param redis_host: Redis host (default: "localhost")
    :param redis_port: Redis port (default: 6379)
    :param redis_db: Redis database number (default: 0)
    :param redis_password(optional): Redis password
    :param username(optional): Redis username
    :param options: Additional options to pass to Redis client

    Examples:
        # Option 1: Create new Redis connection (creates new connection pool)
        ```
        from fastapi_mail.email_utils import DefaultChecker
        import asyncio

        checker = DefaultChecker(db_provider="redis") # if you use redis
        loop = asyncio.get_event_loop()
        loop.run_until_complete(checker.init_redis()) # Connect to redis and create default values
        ```

        # Option 2: Reuse existing Redis client (recommended for better resource management)
        ```
        from redis.asyncio import Redis
        from fastapi_mail.email_utils import DefaultChecker

        # In your app startup
        redis_client = Redis.from_url("redis://localhost:6379/0")

        # Pass existing client to email checker
        checker = DefaultChecker(
            db_provider="redis",
            redis_client=redis_client  # Reuses existing connection pool
        )
        await checker.init_redis()
        ```
    """

    TEMP_EMAIL_DOMAINS: List[str] = []
    BLOCKED_DOMAINS: Set[str] = set()
    BLOCKED_ADDRESSES: Set[str] = set()

    def __init__(
        self,
        source: Optional[str] = None,
        db_provider: Optional[str] = None,
        *,
        redis_client: Optional["aioredis.Redis"] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        username: Optional[str] = None,
        **options: dict,
    ):
        if not redis_lib:
            raise ImportError(
                "You must install redis from https://pypi.org/project/redis in order to run functionality"
            )

        if not request_lib:
            raise ImportError(
                "You must install httpx from https://pypi.org/project/httpx in order to run functionality"
            )

        self.source = (
            source
            or "https://gist.githubusercontent.com/Turall/3f32cb57270aed30d0c7f5e0800b2a92/raw/dcd9b47506e9da26d5772ccebf6913343e53cec9/temporary-email-address-domains"  # noqa: E501
        )
        self.redis_enabled = False

        if db_provider == "redis":
            self.redis_enabled = True
            if redis_client:
                self.redis_client = redis_client
            else:
                self.username = username
                self.redis_host = redis_host
                self.redis_port = redis_port
                self.redis_db = redis_db
                self.redis_password = redis_password
                self.options = options
        self.redis_error_msg = "redis is not connected"

    def catch_all_check(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented"
            f"for class {self.__class__.__name__}"
        )

    async def init_redis(self) -> bool:
        if not self.redis_enabled:
            raise DBProvaiderError(self.redis_error_msg)
        if self.redis_client is None:
            # Create new Redis connection pool
            if not self.username or not self.redis_password:
                self.redis_client = await aioredis.from_url(
                    url="redis://localhost", encoding="UTF-8", **self.options
                )
            else:
                self.redis_client = await aioredis.from_url(
                    url=f"redis://{self.username}:{self.redis_password}@localhost:{self.redis_port}/{self.redis_db}",  # noqa: E501
                    encoding="UTF-8",
                    **self.options,
                )
        else:
            # Validate that the provided client is an async Redis client
            if not isinstance(self.redis_client, aioredis.Redis):
                raise DBProvaiderError(
                    "Provided redis_client must be an async Redis client from redis.asyncio. "
                    f"Received type: {type(self.redis_client)}. "
                    "Use: from redis.asyncio import Redis; client = Redis.from_url(...)"
                )

        temp_counter = await self.redis_client.get("temp_counter")
        domain_counter = await self.redis_client.get("domain_counter")
        blocked_emails = await self.redis_client.get("email_counter")

        if not temp_counter:
            await self.redis_client.set("temp_counter", 0)
        if not domain_counter:
            await self.redis_client.set("domain_counter", 0)
        if not blocked_emails:
            await self.redis_client.set("email_counter", 0)
        temp_domains = await self.fetch_temp_email_domains()
        check_key = await self.redis_client.hgetall("temp_domains")
        if not check_key:
            kwargs = {
                domain: await self.redis_client.incr("temp_counter")
                for domain in temp_domains
            }
            await self.redis_client.hset("temp_domains", mapping=kwargs)

        return True

    def validate_email(self, email: str) -> bool:
        """Validate email address"""
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError:
            raise EmailNotValidError
        return True

    async def fetch_temp_email_domains(self) -> Union[List[str], Any]:
        """Async request to source param resource"""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.source)
            if self.redis_enabled:
                return response.text.split("\n")

            self.TEMP_EMAIL_DOMAINS.extend(response.text.split("\n"))

        return None

    async def blacklist_add_domain(self, domain: str) -> None:
        """Add domain to blacklist"""
        if self.redis_enabled:
            result = await self.redis_client.hget("blocked_domains", domain)
            if not result:
                incr = await self.redis_client.incr("domain_counter")
                await self.redis_client.hset("blocked_domains", domain, incr)
        else:
            self.BLOCKED_DOMAINS.add(domain)

    async def blacklist_rm_domain(self, domain: str) -> None:
        if self.redis_enabled:
            res = await self.redis_client.hdel("blocked_domains", domain)
            if res:
                await self.redis_client.decr("domain_counter")
        else:
            self.BLOCKED_DOMAINS.remove(domain)

    async def blacklist_add_email(self, email: str) -> None:
        """Add email address to blacklist"""
        if self.validate_email(email):
            if self.redis_enabled:
                blocked_domain = await self.redis_client.hget("blocked_emails", email)
                if not blocked_domain:
                    inc = await self.redis_client.incr("email_counter")
                    await self.redis_client.hset("blocked_emails", email, inc)
            else:
                self.BLOCKED_ADDRESSES.add(email)

    async def blacklist_rm_email(self, email: str) -> None:
        if self.redis_enabled:
            res = await self.redis_client.hdel("blocked_emails", email)
            if res:
                await self.redis_client.decr("email_counter")
        else:
            self.BLOCKED_ADDRESSES.remove(email)

    async def add_temp_domain(self, domain_lists: List[str]) -> None:
        """Manually add temporary email"""
        if self.redis_enabled:
            for domain in domain_lists:
                temp_email = await self.redis_client.hget("temp_domains", domain)
                if not temp_email:
                    incr = await self.redis_client.incr("temp_counter")
                    await self.redis_client.hset("temp_domains", domain, incr)
        else:
            self.TEMP_EMAIL_DOMAINS.extend(domain_lists)

    async def blacklist_rm_temp(self, domain: str) -> bool:
        if self.redis_enabled:
            res = await self.redis_client.hdel("temp_domains", domain)
            if res:
                await self.redis_client.decr("temp_counter")
        else:
            self.TEMP_EMAIL_DOMAINS.remove(domain)
        return True

    async def is_disposable(self, email: str) -> bool:
        """Check email address is temporary or not"""
        if self.validate_email(email):
            _, domain = email.split("@")
            result = None
            if self.redis_enabled:
                result = await self.redis_client.hget("temp_domains", domain)
                return bool(result)
            return domain in self.TEMP_EMAIL_DOMAINS
        return False

    async def is_blocked_domain(self, domain: str) -> bool:
        """Check blocked email domain"""
        if not self.redis_enabled:
            return domain in self.BLOCKED_DOMAINS

        blocked_email = await self.redis_client.hget("blocked_domains", domain)
        return bool(blocked_email)

    async def is_blocked_address(self, email: str) -> bool:
        """Check blocked email address"""
        if self.validate_email(email):
            if not self.redis_enabled:
                return email in self.BLOCKED_ADDRESSES

            blocked_domain = await self.redis_client.hget("blocked_emails", email)
            return bool(blocked_domain)
        return False

    async def check_mx_record(
        self, domain: str, full_result: bool = False
    ) -> Union[Dict[str, Any], bool]:
        """Check domain MX records"""
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            return (
                {"port": mx_records.port, "nameserver": mx_records.nameserver}
                if full_result
                else True
            )
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
        ):
            return False

    async def blocked_email_count(self) -> int:
        """count all blocked emails in redis"""
        if self.redis_enabled:
            result = await self.redis_client.get("email_counter")
            if result is not None:
                return result
        return len(self.BLOCKED_ADDRESSES)

    async def blocked_domain_count(self) -> int:
        """count all blocked domains in redis"""
        if self.redis_enabled:
            result = await self.redis_client.get("domain_counter")
            if result is not None:
                return result
        return len(self.BLOCKED_DOMAINS)

    async def temp_email_count(self) -> int:
        """count all temporary emails in redis"""
        if self.redis_enabled:
            result = await self.redis_client.get("temp_counter")
            if result is not None:
                return result
        return len(self.TEMP_EMAIL_DOMAINS)

    async def close_connections(self) -> bool:
        """for correctly close connection from redis"""
        if self.redis_enabled:
            await self.redis_client.close()
            return True
        raise DBProvaiderError(self.redis_error_msg)


class WhoIsXmlApi:
    """
    WhoIsXmlApi class provide working with api  https://www.whoisxmlapi.com/ .
    This service gives free 1000 request to checking email address per month
    ```
    :param token: token you can get from this https://www.whoisxmlapi.com/ link
    :param email: email for checking

    example:
        from email_utils import WhoIsXmlApi

        who_is = WhoIsXmlApi(token="Your access token", email = "your@mailaddress.com")

        print(who_is.smtp_check_())  # check smtp server
        print(who_is.is_disposable()) # check email is disposable or not
        print(who_is.check_mx_record()) # check domain mx records
        print(who_is.free_check()) # check email domain is free or not
    ```
    """

    def __init__(self, token: str, email: str):
        self.token = token
        self.validate_email(email)
        self.email = email
        self.smtp_check = bool()
        self.dns_check = bool()
        self.free_check = bool()
        self.disposable = bool()
        self.catch_all = bool()
        self.mx_records: List[Any] = []
        self.host = "https://emailverification.whoisxmlapi.com/api/v1"

    async def fetch_info(self) -> bool:
        async with httpx.AsyncClient() as client:
            params = {"apiKey": self.token, "emailAddress": self.email}
            response = await client.get(self.host, params=params)

            if response.status_code == 200:
                data = response.json()
                self.smtp_check = data["smtpCheck"]
                self.dns_check = data["dnsCheck"]
                self.free_check = data["freeCheck"]
                self.disposable = data["disposableCheck"]
                self.catch_all = data["catchAllCheck"]
                self.mx_records = data["mxRecords"]

                return True

        raise ApiError(
            "Response status code is {}, error msg {}".format(
                response.status_code, response.text
            )
        )

    def validate_email(self, email: str) -> bool:
        """Validate email address"""

        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError:
            return False
        return True

    def catch_all_check(self) -> bool:
        """
        Tells you whether or not this mail server has a “catch-all” address.
        This refers to a special type of address that can receive emails for any number of
        non-existent email addresses under a particular domain.
        Catch-all addresses are common in businesses where if you send an email to test@hi.com and
        another email to non-existent test2@hi.com, both of those emails will go into the same
        inbox.
        Possible values are 'true' or 'false'. May be 'null' for invalid or non-existing emails.
        """
        return self.catch_all

    def smtp_check_(self) -> bool:
        """
        Checks if the email address exists and
        can receive emails by using SMTP connection and
        email-sending emulation techniques.
        This value will be 'true' if the email address exists and
        can receive email over SMTP, and 'false' if the email address does not exist
        on the target SMTP server or temporarily couldn't receive messages.
        The value will be null if the SMTP request could not be completed,
        mailbox verification is not supported on the target mailbox provider, or not applicable.

        """
        return self.smtp_check

    def is_disposable(self) -> bool:
        """
        Tells you whether or not the email address is disposable (created via a service like
        Mailinator).
        This helps you check for abuse. This value will be 'false' if the email is not disposable,
        and 'true' otherwise.
        May be 'null' for invalid or non-existing emails.

        """
        return self.disposable

    def check_mx_record(self) -> List[Any]:
        """
        Mail servers list.
        May be absent for invalid or non-existing emails.
        """
        return self.mx_records

    def check_dns(self) -> bool:
        """
        Ensures that the domain in the email address, eg: gmail.com, is a valid domain.
        This value will be 'true' if the domain is good and 'false' otherwise.
        May be 'null' for invalid or non-existing emails.

        """
        return self.dns_check

    def check_free(self) -> bool:
        """
        Check to see if the email address is from a free email provider like Gmail or not.
        This value will be 'false' if the email address is not free, and 'true' otherwise.
        May be 'null' for invalid or non-existing emails.

        """
        return self.free_check

    def blacklist_add_email(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented "
            f"for class {self.__class__.__name__}"
        )

    def blacklist_add_domain(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented "
            f"for class {self.__class__.__name__}"
        )

    def add_temp_domain(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented "
            f"for class {self.__class__.__name__}"
        )

    def is_blocked_domain(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented "
            f"for class {self.__class__.__name__}"
        )

    def is_blocked_address(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented "
            f"for class {self.__class__.__name__}"
        )
