### 🕹 Guide

After installing the module and setting up your `FastApi` app:

Main classes and packages are
```FastMail``` ```ConnectionConfig``` ```MessageSchema``` ```email_utils.DefaultChecker``` ```email_utils.WhoIsXmlApi```


### ```FastMail``` class
class has following attributes and methods

-  config  : ConnectionConfig class should be passed in order to establish connection

- send_message : The methods has two attributes, message: MessageSchema, template_name=None
    - message : where you define message sturcture for email
    - template_name : if you are using jinja2 consider template_name as well for passing HTML.


### ```ConnectionConfig``` class
class has following attributes

-  MAIL_USERNAME  : Username for email, some email hosts separates username from the default sender(AWS).
    - If you service does not provide username use sender address for connection.
-  MAIL_PASSWORD : Password for authentication
-  MAIL_SERVER  : SMTP Mail server.
-  MAIL_STARTTLS : For STARTTLS connections
-  MAIL_SSL_TLS : For connecting over TLS/SSL
-  MAIL_DEBUG : Debug mode for while sending mails, defaults 0.
-  MAIL_FROM : Sender address
-  MAIL_FROM_NAME : Title for Mail
-  TEMPLATE_FOLDER: If you are using jinja2, specify template folder name
-  SUPPRESS_SEND:  To mock sending out mail, defaults 0.
-  USE_CREDENTIALS: Defaults to `True`. However it enables users to choose whether or not to login to their SMTP server.
-  VALIDATE_CERTS: Defaults to `True`. It enables to choose whether to verify the mail server's certificate
-  LOCAL_HOSTNAME: It enables to set the hostname of the local machine, which is used to connect to the SMTP server.


### ```MessageSchema``` class
class has following attributes

-  recipients  : List of recipients.
-  attachments : attachments within mail
-  subject  : subject content of the mail
-  body : body of the message
-  cc : cc recipients of the mail
-  bcc : bcc recipients of the mail
-  reply_to : Reply-To recipients in the mail
-  charset : charset defaults to utf-8
-  subtype : subtype of the mail defaults to plain


### ```email_utils.DefaultChecker``` class
Default class for checking email from collected public resource.
The class makes it possible to use redis to save data.

-  source  : `optional` source for collected email data.
-  db_provider  : switch to redis


### ```email_utils.WhoIsXmlApi``` class
WhoIsXmlApi class provide working with api  [WhoIsXmlApi](https://www.whoisxmlapi.com)
This service gives free 1000 requests for checking email address per month.

-  token  : token you can get from this [WhoIsXmlApi](https://www.whoisxmlapi.com) link
-  email  : email for checking