import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import utils


class EmailSender:
    def __init__(self, server, port=465):
        self.server = smtplib.SMTP(server, port)

    def login(self, username, password):
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(username, password)

    def send(self, fromaddr, toaddr, ccaddr, subject, body):
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = utils.extract_addr(toaddr)
        msg['Cc'] = ccaddr
        msg['Subject'] = "%s" % Header(subject, 'utf-8')
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        text = msg.as_string()
        self.server.sendmail(fromaddr, [toaddr, ccaddr], text)
