# mailbox content handler

import imaplib
import email
import email.header
import datetime
from collections import namedtuple

MailAttachment = namedtuple('MailAttachment', ['filename', 'content_type', 'content'])


class MailboxError(Exception):
    def __init__(self, msg):
        Exception(msg)


class LoginError(MailboxError):
    def __init__(self, msg):
        MailboxError(msg)


class FolderNotFoundError(MailboxError):
    def __init__(self, msg):
        MailboxError(msg)


class MailboxMessage:
    def __init__(self, folder, num, msg):
        self.num = num
        self.folder = folder
        self.msg = msg

        decode = email.header.decode_header(msg['Subject'])[0]
        self.subject = unicode(decode[0].decode('utf-8'))

        decode = email.header.decode_header(msg['From'])[0]
        self.sender = unicode(decode[0].decode('utf-8'))

        # Now convert to local date-time
        self.raw_date = msg['Date']
        date_tuple = email.utils.parsedate_tz(self.raw_date)
        if date_tuple:
            self.local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

    def attachments(self):
        if self.msg.get_content_maintype() == 'multipart':
            for part in self.msg.walk():
                yield MailAttachment(part.get_filename(), part.get_content_type(), part.get_payload(decode=1) or '')

    def __str__(self):
        return 'imap(%s:id=%s, sender="%s", subject="%s", date="%s")' % \
               (self.folder, self.num, self.sender, self.subject, self.local_date)


class MailboxHandler:
    def __init__(self, imap_server):
        self.conn = imaplib.IMAP4_SSL(imap_server)

    def login(self, mail, password):
        try:
            self.conn.login(mail, password)
        except imaplib.IMAP4.error:
            raise LoginError('failed to login to %s' % mail)

    def get_message(self, folder):
        rv, data = self.conn.select(folder)
        if rv != 'OK':
            raise FolderNotFoundError("Can't select folder %s" % folder)

        rv, data = self.conn.search(None, 'ALL')
        if rv != 'OK':
            raise MailboxError("Can't retrieve new messages")

        for num in data[0].split():
            rv, raw_msg = self.conn.fetch(num, '(RFC822)')
            if rv != 'OK':
                raise MailboxError("Can't retrieve message %s" % num)

            msg = email.message_from_string(raw_msg[0][1])
            return MailboxMessage(folder, num, msg)

    def move_message(self, msg, dst_folder):
        msg_id = msg.num
        self.conn.copy(msg_id, dst_folder)
        self.conn.store(msg_id, '+FLAGS', '\\Deleted')
        self.conn.expunge()

    def logout(self):
        self.conn.logout()
