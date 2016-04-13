import subprocess
import tempfile
import logging
import re
import utils


class MessageHandler:
    def __init__(self, cfg):
        self.cfg = cfg
        self.out = None

    def _exec(self, packfile):
        proc = subprocess.Popen([self.cfg.checker_exec, packfile],
                                stdin=utils.get_dev_null(), stdout=subprocess.PIPE)
        self.out = proc.communicate()[0]
        return proc.wait()

    @staticmethod
    def is_archive_file(fname):
        return re.match(r'.*(\.tar\.gz|\.tgz|\.tar|\.tar.bz2)$', fname, flags=re.IGNORECASE)

    def handle(self, msg):
        archive = None
        for att in msg.attachments():
            logging.info('---- attach: %s (%s) %d bytes', att.filename, att.content_type, len(att.content))
            if att.filename and MessageHandler.is_archive_file(att.filename):
                archive = att
                break

        if archive is None:
            logging.info('skip message (no appropriate attachment found)')
            return -1

        tf = tempfile.NamedTemporaryFile(suffix='_%s' % archive.filename, delete=True)
        tf.write(archive.content)
        tf.flush()
        rv = self._exec(tf.name)
        tf.close()

        return rv
