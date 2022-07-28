# Fastapi-mail

The fastapi-mail simple lightweight mail system, sending emails and attachments(individual && bulk)


[![MIT licensed](https://img.shields.io/github/license/sabuhish/fastapi-mail)](https://raw.githubusercontent.com/sabuhish/fastapi-mail/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/sabuhish/fastapi-mail.svg)](https://github.com/sabuhish/fastapi-mail/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/sabuhish/fastapi-mail.svg)](https://github.com/sabuhish/fastapi-mail/network)
[![GitHub issues](https://img.shields.io/github/issues-raw/sabuhish/fastapi-mail)](https://github.com/sabuhish/fastapi-mail/issues)
[![Downloads](https://pepy.tech/badge/fastapi-mail)](https://pepy.tech/project/fastapi-mail)



## Using Jinja2 HTML Templates

In order to use Jinja template langauge, your must specify email folder within your applications working directory.

In sending HTML emails, the CSS expected by mail servers -outlook, google, etc- must be inline CSS. Fastapi mail passes _"body"_ to the rendered template. In creating the template for emails the dynamic objects should be used with the assumption that the variable is named "_body_" and that it is a python dict.

check out jinja2 for more details 
[jinja2](https://jinja.palletsprojects.com/en/2.11.x/)



##  Guide for Email Utils

The utility allows you to check temporary email addresses, you can block any email or domain. 
You can connect Redis to save and check email addresses. If you do not provide a Redis configuration, 
then the utility will save it in the list or set by default.



## Writing unittests using Fastapi-Mail
Fastapi mails allows you to write unittest for your application without sending emails to
non existent email address by mocking the email to be sent. To mock sending out mails, set
the suppress configuration to true. Suppress send defaults to False to prevent mocking within applications.


## Support for Reply-To header is added
Use this just like bcc but to specify addresses that should receive a reply to your message. E-mail systems MAY respect this as per RFC 2822.
