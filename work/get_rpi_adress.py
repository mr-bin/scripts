#!/usr/bin/python2

import re
import smtplib
import urllib2
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders

def get_external_ip(html):
    grab = re.findall('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', html)
    address = grab[0]
    return address

html = urllib2.urlopen('http://yandex.ru/internet').read()
address = get_external_ip(html)

msg = MIMEMultipart('alternative')
msg['Subject'] = "rpi address: %s" % address
msg['From'] = sender = 'ZZZ@mail.ru'
msg['To'] = reciever = 'XXX@gmail.com'

html = """
<a href="http://%s"> Home accounting </a> <br/> 
<a href="http://%s:8080"> Bookcase </a>
"""

part = MIMEText(html % (address, address), 'html')
msg.attach(part)

files_for_backup=[
'/home/ansible/bookcase/db/bookcase.sqlite',
'/home/ansible/home-accounting/db/accounting.sqlite'
]

for one in files_for_backup:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(one, "rb").read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"'%basename(one))
    msg.attach(part)

s = smtplib.SMTP_SSL('smtp.mail.ru')
s.login('XXX', 'XXX')
s.sendmail(sender, reciever, msg.as_string())
s.close()

