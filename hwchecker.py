#!/usr/bin/env python

import getpass
import argparse
import tempfile
import hwck
import time
from hwck import *


def parse_command_line():
    parser = argparse.ArgumentParser(description='Grab new emails and automatically check assignments')
    parser.add_argument('-c', '--config', metavar='config_file', type=str, required=True, help='path to config file')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', help='be verbose (-vv increase it more)')
    return parser.parse_args()


def handle_new_messages(cfg):
    cfg.add_to_log('Logging to server {} (user={})'.format(cfg.imap_server, cfg.username))
    mb = mbhandler.MailboxHandler(cfg.imap_server, cfg.username, cfg.password)
    cfg.add_to_log('Login success')

    empty_dir = 0
    while True:
        for hw_id in cfg.homeworks.keys():
            cfg.create_folders(hw_id)
            msg = mb.get_message(cfg, hw_id)
            if not msg:
                empty_dir += 1
                cfg.add_to_log('No more messages to proceed for {}'.format(hw_id))
                if empty_dir >= len(cfg.homeworks):
                    time.sleep(cfg.check_interval)
                    cfg.add_to_log('Extra sleep')
                time.sleep(cfg.check_interval)
                continue

            empty_dir = 0

            cfg.add_to_log('new message from {}: {}'.format(msg.sender.encode("utf-8"), msg.subject.encode("utf-8")))
            mhandler = mhandle.MessageHandler(cfg, hw_id)
            rc = mhandler.handle(msg)

            cfg.add_to_log('handling finished with code {}'.format(rc))
            #msender = sending.EmailSender(cfg.smtp_server)
            #msender.login(cfg.addr, cfg.password)

            tf = tempfile.NamedTemporaryFile(suffix='_%s' % hw_id, delete=False, dir="/tmp/hw_logs/")
            if rc == 0:
                #msender.send(fromaddr=cfg.addr, toaddr=msg.sender, ccaddr=cfg.addr,
                #             subject="RESULT: " + msg.subject, body=mhandler.out)
                tf.write(mhandler.out)
                #mb.move_message(msg, cfg.ok_folder)
                cfg.add_to_log("{} --- ok".format(msg.sender.encode("utf-8")))
            else:
                #msender.send(fromaddr=cfg.addr, toaddr=msg.sender, ccaddr=cfg.addr,
                #             subject="ERROR: " + msg.subject, body='cant find attachment or exec container')
                tf.write('cant find attachment or exec container')
                #mb.move_message(msg, cfg.err_folder)
                cfg.add_to_log("{} --- fail".format(msg.sender.encode("utf-8")))
            tf.flush()
            cfg.add_to_log("log: {}".format(tf.name))
            tf.close()

            time.sleep(cfg.check_interval)


def check_mail(cfg):
        try:
            handle_new_messages(cfg)
        except RuntimeError as e:
            cfg.add_to_log("Error occured: {}".format(e))


def main():
    args = parse_command_line()
    hwck.init_logger(args.verbose)

    cfg = config.HwckConfig(args.config)

    if not cfg.password:
        cfg.password = getpass.getpass(prompt='Enter password for %s' % cfg.username)

    check_mail(cfg)


if __name__ == '__main__':
    main()
