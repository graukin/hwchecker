#!/usr/bin/env python

import getpass
import argparse
import logging
import hwck
import time
from hwck import *


def parse_command_line():
    parser = argparse.ArgumentParser(description='Grab new emails and automatically check assignments')
    parser.add_argument('-c', '--config', metavar='config_file', type=str, required=True, help='path to config file')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', help='be verbose (-vv increase it more)')
    return parser.parse_args()


def handle_new_messages(cfg):
    logging.debug('Logging to server %s (user=%s)', cfg.imap_server, cfg.username)
    mb = mbhandler.MailboxHandler(cfg.imap_server, cfg.username, cfg.password)
    logging.info('Login success')

    current_hw_id = 0
    empty_dir = 0
    while True:
        cfg.create_folders(current_hw_id)
        current_hw_id += 1
        msg = mb.get_message(cfg.src_folder)
        if not msg:
            empty_dir += 1
            logging.info('No more messages to proceed')
            if empty_dir >= len(cfg.homeworks):
                time.sleep(cfg.check_interval)
                logging.info('Extra sleep')
            time.sleep(cfg.check_interval)
            continue

        empty_dir = 0

        logging.info('new message: %s', msg)
        mhandler = mhandle.MessageHandler(cfg)
        rc = mhandler.handle(msg)

        logging.info('handling finished with code %d', rc)
        msender = sending.EmailSender(cfg.smtp_server)
        msender.login(cfg.from_addr, cfg.password)

        if rc == 0:
            msender.send(fromaddr=cfg.from_addr, toaddr=msg.sender, ccaddr=cfg.cc_addr,
                         subject="RESULT: " + msg.subject, body=mhandler.out)

            mb.move_message(msg, cfg.ok_folder)
        else:
            msender.send(fromaddr=cfg.from_addr, toaddr=msg.sender, ccaddr=cfg.cc_addr,
                         subject="ERROR: " + msg.subject, body='cant find attachment or exec container')

            mb.move_message(msg, cfg.err_folder)

        time.sleep(cfg.check_interval)


def check_mail(cfg):
        try:
            handle_new_messages(cfg)
        except RuntimeError as e:
            logging.error("Error occured: %s", e)


def main():
    args = parse_command_line()
    hwck.init_logger(args.verbose)

    logging.info('Loading config from %s', args.config)
    cfg = config.HwckConfig(args.config)

    if not cfg.password:
        cfg.password = getpass.getpass(prompt='Enter password for %s' % cfg.username)

    check_mail(cfg)


if __name__ == '__main__':
    main()
