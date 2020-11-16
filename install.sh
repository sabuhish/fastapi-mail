#!/bin/bash

# Installing dependencies for fastapi-mail, thanks for contirbuting if you have any issues feel free to open.
# Issue URL https://github.com/sabuhish/fastapi-mail/issues


set -e

CURRENT_DIRECTORY=$(pwd)

CURRENT_USER=$(whoami)
VERSION="0.3.0.2"

README_URL="https://github.com/sabuhish/fastapi-mail"

echo -e "Staring to create environment and installing dependencies for fastapi-mail"

function install(){

    sudo -u $CURRENT_USER bash << EOF 
        echo -e "\ncreating virtualenv ..."
        
        python3 -m venv .venv
        source .venv/bin/activate
        python --version
        
        pip install --upgrade pip

        echo "installing dependencies"

        pip install "fastapi>=0.61.2" 'jinja2>=2.11.2' "aiosmtplib>=1.1.4" "python-multipart>=0.0.5" "pydantic>=1.7.1" "email-validator>=1.1.1"
            
       
        touch $CURRENT_DIRECTORY/main.py


        echo "
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
import asyncio


conf = ConnectionConfig(
    MAIL_USERNAME = 'YourUsername',
    MAIL_PASSWORD = 'strong_password',
    MAIL_FROM = 'your@email.com',
    MAIL_PORT = '587',
    MAIL_SERVER = 'your mail server',
    MAIL_TLS = True,
    MAIL_SSL = False
)


html = '<p>Hi this test mail, thanks for using Fastapi-mail</p>' 

message = MessageSchema(
        subject='Fastapi-Mail module',
        recipients=['recipients'],  # List of recipients, as many as you can pass 
        body=html,
        subtype='html'
        )

fm = FastMail(conf)

loop = asyncio.get_event_loop()
task = loop.create_task(fm.send_message(message,template_name="email_template.html"))

loop.run_until_complete(task)
loop.close()" >> main.py
        
        echo ""
        echo -e "fastapi-mail: $VERSION"
      
        echo -e "\nYou are ready to work on it, do the last things:"
        echo -e "source .venv/bin/activate"
        echo -e "cat main.py"
      

        echo -e "\nPlease see the README file for more information:"
        echo -e "$README_URL\n\n"
        exit 0

EOF

}

install

