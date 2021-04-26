import dns.resolver
import dns.exception
import httpx
import inspect
import aioredis
from .errors import ApiError, DBProvaiderError
from pydantic import EmailStr
from abc import ABC, abstractmethod


class AbstractEmailChecker(ABC):
    @abstractmethod
    def validate_email(self):
        pass

    @abstractmethod
    def is_dispasoble(self):
        pass

    @abstractmethod
    def check_mx_record(self):
        pass

    @abstractmethod
    def blacklist_add_email(self):
        pass

    @abstractmethod
    def blacklist_add_domain(self):
        pass

    @abstractmethod
    def add_temp_domain(self):
        pass

    @abstractmethod
    def is_blocked_domain(self):
        pass

    @abstractmethod
    def is_blocked_address(self):
        pass

    @abstractmethod
    def catch_all_check(self):
        pass


class DefaultChecker(AbstractEmailChecker):

    """
        Default class for checking email from collected public resource.
        The class makes it possible to use redis to save data.
        ```
        :param source(optional): source for collected email data.
        :param db_provider: switch to redis

        example: 
            from email_utils import DefaultChecker
            import asyncio

            a = DefaultChecker(db_provider="redis") # if you use redis
            loop = asyncio.get_event_loop()
            loop.run_until_complete(a.init_redis()) # Connect to redis and create default values
        ```
    """
    TEMP_EMAIL_DOMAINS = []
    BLOCKED_DOMAINS = set()
    BLOCKED_ADDRESSES = set()

    def __init__(
        self,
        source: str = None,
        db_provider: str = None,
        *,
        redis_host: str = "redis://localhost",
        redis_port: str = 6379,
        redis_db: int = 0,
        redis_pass: str = None,
        **options: dict,
    ):

        self.source = (
            source
            or "https://gist.githubusercontent.com/Turall/3f32cb57270aed30d0c7f5e0800b2a92/raw/dcd9b47506e9da26d5772ccebf6913343e53cec9/temporary-email-address-domains"
        )
        self.redis_enabled = False

        if db_provider == "redis":
            self.redis_enabled = True
            self.redis_host = redis_host
            self.redis_port = redis_port
            self.redis_db = redis_db
            self.redis_pass = redis_pass
            self.options = options
        self.redis_error_msg = "redis is not connected"

    def catch_all_check(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented for class {self.__class__.__name__}"
        )

    async def init_redis(self):
        if not self.redis_enabled:
            raise DBProvaiderError(self.redis_error_msg)
        if not hasattr(self, "redis_client"):
            self.redis_client = await aioredis.create_redis_pool(
                address=f"{self.redis_host}:{self.redis_port}",
                db=self.redis_db,
                password=self.redis_pass,
                encoding="UTF-8",
                **self.options
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
            kwargs = {domain: await self.redis_client.incr("temp_counter") for domain in temp_domains}
            await self.redis_client.hmset_dict("temp_domains", kwargs)

        return True

    def validate_email(self, email: str):
        """ Validate email address """
        if EmailStr.validate(email):
            return True

    async def fetch_temp_email_domains(self):
        """ Async request to source param resource """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.source)
            if self.redis_enabled:
                return response.text.split("\n")

            self.TEMP_EMAIL_DOMAINS.extend(response.text.split("\n"))

    async def blacklist_add_domain(self, domain: str):
        """ Add domain to blacklist """
        if self.redis_enabled:
            result = await self.redis_client.hget("blocked_domains", domain)
            if not result:
                incr = await self.redis_client.incr("domain_counter")
                await self.redis_client.hset("blocked_domains", domain, incr)
        else:
            self.BLOCKED_DOMAINS.add(domain)

        return True

    async def blacklist_rm_domain(self, domain: str):
        if self.redis_enabled:
            res = await self.redis_client.hdel("blocked_domains", domain)
            if res:
                await self.redis_client.decr("domain_counter")
        else:
            self.BLOCKED_DOMAINS.remove(domain)
        return True

    async def blacklist_add_email(self, email: str):
        """ Add email address to blacklist """
        if self.validate_email(email):
            if self.redis_enabled:
                blocked_domain = await self.redis_client.hget("blocked_emails", email)
                if not blocked_domain:
                    inc = await self.redis_client.incr("email_counter")
                    await self.redis_client.hset("blocked_emails", email, inc)
            else:
                self.BLOCKED_ADDRESSES.add(email)
            return True

    async def blacklist_rm_email(self, email: str):
        if self.redis_enabled:
            res = await self.redis_client.hdel("blocked_emails", email)
            if res:
                await self.redis_client.decr("email_counter")
        else:
            self.BLOCKED_ADDRESSES.remove(email)
        return True

    async def add_temp_domain(self, domain_lists: list):
        """ Manually add temporary email """
        if self.redis_enabled:
            for domain in domain_lists:
                temp_email = await self.redis_client.hget("temp_domains", domain)
                if not temp_email:
                    incr = await self.redis_client.incr("temp_counter")
                    await self.redis_client.hset("temp_domains", domain, incr)
        else:
            self.TEMP_EMAIL_DOMAINS.extend(domain_lists)
        return True

    async def blacklist_rm_temp(self, domain: str):
        if self.redis_enabled:
            res = await self.redis_client.hdel("temp_domains", domain)
            if res:
                await self.redis_client.decr("temp_counter")
        else:
            self.TEMP_EMAIL_DOMAINS.remove(domain)
        return True

    async def is_dispasoble(self, email: str):
        """ Check email address is temporary or not """
        if self.validate_email(email):
            _, domain = email.split("@")
            result = None
            if self.redis_enabled:
                result = await self.redis_client.hget("temp_domains", domain)
                return bool(result)
            return domain in self.TEMP_EMAIL_DOMAINS

    async def is_blocked_domain(self, domain: str):
        """ Check blocked email domain"""
        if not self.redis_enabled:
            return domain in self.BLOCKED_DOMAINS

        blocked_email = await self.redis_client.hget("blocked_domains", domain)
        return bool(blocked_email)

    async def is_blocked_address(self, email: str):
        """ Check blocked email address"""
        if self.validate_email(email):
            if not self.redis_enabled:
                return email in self.BLOCKED_ADDRESSES

            blocked_domain = await self.redis_client.hget("blocked_emails", email)
            return bool(blocked_domain)

    async def check_mx_record(self, domain: str, full_result: bool = False):
        """ Check domain MX records """

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

    async def blocked_email_count(self):
        """ count all blocked emails in redis """
        if self.redis_enabled:
            return await self.redis_client.get("email_counter")
        return len(self.BLOCKED_ADDRESSES)

    async def blocked_domain_count(self):
        """ count all blocked domains in redis """
        if self.redis_enabled:
            return await self.redis_client.get("domain_counter")
        return len(self.BLOCKED_DOMAINS)

    async def temp_email_count(self):
        """ count all temporary emails in redis """
        if self.redis_enabled:
            return await self.redis_client.get("temp_counter")
        return len(self.TEMP_EMAIL_DOMAINS)

    async def close_connections(self):
        """ for correctly close connection from redis """
        if self.redis_enabled:
            self.redis_client.close()
            await self.redis_client.wait_closed()
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
            print(who_is.is_dispasoble()) # check email is disposable or not
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
        self.mx_records = []
        self.host = "https://emailverification.whoisxmlapi.com/api/v1"

    async def fetch_info(self):
        async with httpx.AsyncClient() as client:
            params = {"apiKey": self.token, "emailAddress": self.email}
            response = await client.get(self.host, params=params)

            if response.status_code == 200:
                data = response.json
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

    def validate_email(self, email: str):
        """ Validate email address """
        if EmailStr.validate(email):
            return True

    def catch_all_check(self):
        """
        Tells you whether or not this mail server has a “catch-all” address. 
        This refers to a special type of address that can receive emails for any number of non-existent email addresses 
        under a particular domain. Catch-all addresses are common in businesses where if you send an email to test@hi.com and 
        another email to non-existent test2@hi.com, both of those emails will go into the same inbox. 
        Possible values are 'true' or 'false'. May be 'null' for invalid or non-existing emails.

        """
        return self.catch_all

    def smtp_check_(self):
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

    def is_dispasoble(self):
        """
        Tells you whether or not the email address is disposable (created via a service like Mailinator). 
        This helps you check for abuse. This value will be 'false' if the email is not disposable, and 'true' otherwise. 
        May be 'null' for invalid or non-existing emails.

        """
        return self.disposable

    def check_mx_record(self):
        """
        Mail servers list. 
        May be absent for invalid or non-existing emails.    
        """
        return self.mx_records

    def check_dns(self):
        """
        Ensures that the domain in the email address, eg: gmail.com, is a valid domain. 
        This value will be 'true' if the domain is good and 'false' otherwise. 
        May be 'null' for invalid or non-existing emails.

        """
        return self.dns_check

    def check_free(self):
        """
        Check to see if the email address is from a free email provider like Gmail or not. 
        This value will be 'false' if the email address is not free, and 'true' otherwise. 
        May be 'null' for invalid or non-existing emails.

        """
        return self.free_check

    def blacklist_add_email(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented for class {self.__class__.__name__}"
        )

    def blacklist_add_domain(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented for  class {self.__class__.__name__}"
        )

    def add_temp_domain(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented for class {self.__class__.__name__}"
        )

    def is_blocked_domain(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented for class {self.__class__.__name__}"
        )

    def is_blocked_address(self):
        raise NotImplementedError(
            f"Func named {inspect.currentframe().f_code.co_name} not implemented for class {self.__class__.__name__}"
        )
