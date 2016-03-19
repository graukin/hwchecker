import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    def __init__(self, server, port=587):
        self.server = smtplib.SMTP(server, port)

    def login(self, username, password):
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(username, password)

    def send(self, fromaddr, toaddr, ccaddr, subject, body):
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Cc'] = ccaddr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        self.server.sendmail(fromaddr, [toaddr, ccaddr], text)
