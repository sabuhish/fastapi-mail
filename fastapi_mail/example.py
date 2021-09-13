import asyncio

from fastapi_mail.email_utils import DefaultChecker, WhoIsXmlApi

checker = DefaultChecker(db_provider='redis')
loop = asyncio.get_event_loop()
loop.run_until_complete(checker.init_redis())
res = loop.run_until_complete(checker.blacklist_rm_temp('promail1.net'))
print(res)
res = loop.run_until_complete(checker.temp_email_count())
loop.run_until_complete(checker.close_connections())


who_is = WhoIsXmlApi(token='Your access token', email='your@mailaddress.com')

print(who_is.smtp_check_())  # check smtp server
print(who_is.is_dispasoble())   # check email is disposable or not
print(who_is.check_mx_record())   # check domain mx records
print(who_is.free_check)   # check email domain is free or not
