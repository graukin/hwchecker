#!/usr/bin/env python

import getpass
import argparse
import logging
import hwck
from hwck import *


def parse_command_line():
    parser = argparse.ArgumentParser(description='Grab new emails and handle them')
    parser.add_argument('-u', '--user', metavar='name@domain', type=str, required=True, help='your mail address')
    parser.add_argument('-s', '--server', metavar='address', type=str, required=True, help='address of IMAP server')
    parser.add_argument('--smtp', metavar='address', type=str, required=True, help='address of SMTP server')
    parser.add_argument('-p', '--password', type=str, metavar='password',
                        help='password (only for debug, better leave empty)')
    parser.add_argument('-e', '--execute', type=str, required=True, help='execute given script (file subject as params)')
    parser.add_argument('-f', '--folder', type=str, default='INBOX', help='folder to process')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', help='be verbose (-vv increase it more)')
    parser.add_argument('--ok-folder', type=str, required=True, help='folder for OK messages')
    parser.add_argument('--err-folder', type=str, required=True, help='folder for ERR messages')
    args = parser.parse_args()

    return args


def main():
    args = parse_command_line()
    hwck.init_logger(args.verbose)

    if not args.password:
        args.password = getpass.getpass(prompt='Enter password for %s' % args.mailbox)

    while True:
        mb = mbhandler.MailboxHandler(args.server, args.user, args.password)
        logging.debug('Logging to %s (server=%s)', args.user, args.server)
        logging.info('Login success (%s)', args.user)

        msg = mb.get_message(args.folder)
        if not msg:
            logging.info('No more messages to proceed')
            break

        logging.info('new message: %s', msg)
        mhandler = mhandle.MessageHandler(args)
        rc = mhandler.handle(msg)

        logging.info('handling finished with code %d', rc)
        msender = sending.EmailSender(args.smtp)
        msender.login('ts2016dups@mail.ru', args.password)

        if rc == 0:
            msender.send(fromaddr='ts2016dups@mail.ru', toaddr=msg.sender, ccaddr='ts2016dups@mail.ru',
                         subject="RESULT: " + msg.subject, body=mhandler.out)

            mb.move_message(msg, args.ok_folder)
        else:
            msender.send(fromaddr='ts2016dups@mail.ru', toaddr=msg.sender, ccaddr='ts2016dups@mail.ru',
                         subject="ERROR: " + msg.subject, body='cant find attachment or exec container')

            mb.move_message(msg, args.err_folder)


if __name__ == '__main__':
    main()
