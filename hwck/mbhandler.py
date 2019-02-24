# mailbox content handler

import imaplib
import email
import email.header
from email.parser import HeaderParser
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
        self.msg = email.message_from_string(msg)

        parser = HeaderParser()
        hdr = parser.parsestr(msg)

        self.subject = MailboxMessage.decode_header(hdr['Subject'])
        self.sender = MailboxMessage.decode_header(hdr['From'])

        # Now convert to local date-time
        self.raw_date = hdr['Date']
        date_tuple = email.utils.parsedate_tz(self.raw_date)
        if date_tuple:
            self.local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

    @staticmethod
    def decode_header(hdr):
        return unicode(email.header.make_header(email.header.decode_header(hdr)))

    def attachments(self):
        if self.msg.get_content_maintype() == 'multipart':
            for part in self.msg.walk():
                fname = MailboxMessage.decode_header(part.get_filename()) if part.get_filename() else None
                yield MailAttachment(fname, part.get_content_type(), part.get_payload(decode=1) or '')

    def __str__(self):
        return 'imap(%s:id=%s, sender="%s", subject="%s", date="%s")' % \
               (self.folder, self.num, self.sender, self.subject, self.local_date)


class MailboxHandler:
    def __init__(self, imap_server, mail, password):
        self.imap_server = imap_server
        self.conn = None
        self.mail = mail
        self.password = password

        self.login()

    def login(self):
        if self.conn:
            self.conn.logout()

        self.conn = imaplib.IMAP4_SSL(self.imap_server)

        try:
            self.conn.login(self.mail, self.password)
        except imaplib.IMAP4.error:
            raise LoginError('failed to login to %s' % self.mail)

    def _relogin(self):
        self.login()

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

            return MailboxMessage(folder, num, raw_msg[0][1])
        return None

    def move_message(self, msg, dst_folder):
        self._relogin()
        rv, data = self.conn.select(msg.folder)
        if rv != 'OK':
            raise FolderNotFoundError("Can't select folder %s" % msg.folder)

        msg_id = msg.num
        self.conn.copy(msg_id, dst_folder)
        self.conn.store(msg_id, '+FLAGS', '\\Deleted')
        self.conn.expunge()

    def logout(self):
        self.conn.logout()
