import smtplib, os, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.utils import formatdate, make_msgid
from fastapi import UploadFile
from fastapi_mail.version import PY3
from fastapi_mail.errors import TypeExecption, NotAvilableService, WrongPort, WrongFormat, WrongFile, ConnectionErrors


class FastMail: 

    """
        Fastapi mail system sending mails(individual, bulk) attachments(individual, bulk)

        The class object holds session information necesseary to initilize object.
        param :: email : email address to connect your mail server
        type  :: email: str
        param :: password : password of mail address 
        type  :: password : str 
        param :: port : port to be used in connection, read your mail-server documentation to know which port use, default to 587
        type  :: port : str or int
        param :: service : the service is mail domain to be used to establish connection
        type  :: tls : bool
        type  :: ssl : bool
        param :: custom : if you set custom True, you need to pass port and services argument (**kwargs, see example) your mail domain 
        type  :: custom : bool 
    """

    __smtp_ports = ["587","465","25","2525"]

    __services = {"gmail":"smtp.gmail.com","yahoo":"smtp.mail.yahoo.com","mailru":"smtp.mail.ru","yandex":"smtp.yandex.com"}

    __text_format = ["html", "plain"]


    def __enter__(self):
        self.__configure_connection()
    

    def __exit__(self, typ, value, tb):
        self.session.quit()


    def __str__(self):
        return self.message.as_string()


    def __init__(self,
        email: str,
        password: str,
        port: str = "587",
        service: str ="gmail",
        tls: bool = False,
        ssl: bool = False,
        custom: bool= False,
        **kwrags):

        self._email =  email
        self._password= password
        self._ssl = ssl
        self._tls = tls
        self.custom = custom
        self.msgId = make_msgid()
        self.message = MIMEMultipart()


        if not self.custom:

            self._port = str(port)            
            self._service = service
            
            if type(self._port)not in [str, int]:
                raise TypeExecption(f"{self._port} port must be either string or integer")
        
                
            if self._port not in self.__smtp_ports:
                raise WrongPort("wrong port number",f"Port number should be one of these {self.__smtp_ports}")

        
        else:
            self._port = str(port)            
            self._service = kwrags.get("services")


 
    async def send_message(self,recipient: str, subject: str ,body: str ,text_format: str ="plain", Bcc: str = None, file: UploadFile = None, bulk: bool = False):
        """ 
            Sending mail
            param :: recipient : receiver
            type  :: recipient : str

            param :: subject : subject for mail
            type  :: subject : str

            param :: body : body of the message
            type  :: body : str

            param :: text_format : text format of the mail content, default plain. HTML and plain available
            type  :: text_format : str

            param :: Bcc : Bcc of the mail
            type  :: Bcc : str

            param :: file : Bcc of the mail
            type  :: file : byte

            param :: bulk : bulk is default False, if you want send bulk mail set this True.(see example)
            type  :: bulk : bool

        """
        
        TO = recipient if type(recipient) is list else [recipient]
       
        if text_format not in self.__text_format:
            raise WrongFormat(f"{text_format} not possible", f'avaliable ones are {self.__text_format}')
        if bulk:

            if isinstance(recipient, str):
                raise TypeExecption(f"{recipient} argument must be a list")
            
            if len(recipient)==1:
                raise TypeExecption(f"if bulk is True,{recipient} cannot be 1. Should be more than one")
            

            if not file:

                return await self.__send_bulk(recipient,subject,body,text_format)
         
            return await self.__send_bulk(recipient,subject,body,text_format,file)
            
        
        
        self.message["From"] = self._email
        self.message["To"] = ", ".join(TO)
        self.message["Subject"] = subject
        self.message['Date'] = formatdate(time.time(), localtime=True)
        self.message['Message-ID'] = self.msgId

        if Bcc:
            self.message["Bcc"] = Bcc 
           
        message_form = MIMEText(body, text_format)
        self.message.attach(message_form)
 
        if file:
            await  self.__attach_file(file,self.message)
         
        return await self.__send(recipient,self.message)

    async def __send(self,recipient: str, message: str) -> bool:

        self.__configure_connection()
        self.session.sendmail(self._email,recipient,message.as_string())
        self.session.quit()
        
        return True


    async def __send_bulk(self,TO: str, subject: str, body: str, text_format: str, file: UploadFile=None):
        

        if file:
            await self.__attach_file(file,self.message)
       
        
        self.message["From"] = self._email
        self.message["Subject"] = subject
        message_form = MIMEText(body, text_format)
        self.message.attach(message_form) 

        try:
            with self.__configure_connection() as conn:
                for recieptent in TO:
                    email = recieptent.split()
                    del self.message['To']
                
                    self.message["To"] = ", ".join(email)

                    print("Bulk mail sending to",self.message["To"])

                    conn.sendmail(self._email,[recieptent],self.message.as_string())
                    
        except Exception as err:
            raise ConnectionErrors(f"Exception rised {err} check connection") 

        return True
          
    
    
    async  def __attach_file(self, file: UploadFile, message: str) -> bool:
        try:
            if isinstance(file, list):
                attachments = file
            else:
                attachments = [file]


            for attachment in attachments:
                f = MIMEBase(*attachment.content_type.split('/'))
                
                f.set_payload(await attachment.read())
                encode_base64(f)

                filename = attachment.filename

                try:
                    filename and filename.encode('ascii')
                except UnicodeEncodeError:
                    if not PY3:
                        filename = filename.encode('utf8')
                filename = ('UTF8', '', filename)
                

                f.add_header('Content-Disposition',
                            "attachment",
                            filename=filename)
                

                self.message.attach(f)

            return self.message.attach(f)


        except Exception as err:
            print(err)

            raise WrongFile(f"{err}", "is not a file, make sure you provide a file")


    def __configure_connection(self):

        if not self.custom:
            for avaliable_services in self.__services.keys():
                avaliable =  avaliable_services ==self._service
                
                if avaliable:
                        break
                        
            if not avaliable:
                raise NotAvilableService("error",f"The service {self._service} is not avalibale, Currently  only these {self.__services} services avalibale, if you require custom then make sure you do custom=True")

        if self._ssl:
            try:
                if not self.custom:
                    session = smtplib.SMTP_SSL(f"{self.__services.get(self._service)}:{self._port}")
                
                else:
                    session = smtplib.SMTP_SSL(f"{self._service}:{self._port}")

                if self._tls:

                    session.starttls()

                session.ehlo()
                session.login(self._email, self._password)
                self.session = session
                
                return self.session

            except Exception as error:

                raise ConnectionErrors(f"Exception rised {error} check connection") 

        else:
            try:
                if not self.custom:

                    session = smtplib.SMTP(f"{self.__services.get(self._service)}:{self._port}")

                else:
                    print(f"{self._service}:{self._port}")

                    session = smtplib.SMTP(f"{self._service}:{self._port}")
                    
                if self._tls:

                    session.starttls()
                
                session.ehlo()
                session.login(self._email, self._password)
                self.session = session
                
                return self.session

                
            except Exception as error:
                print("error",error)

                raise ConnectionErrors(f"Exception rised {error} check connection") 