import subprocess
import tempfile
import re
import utils


class MessageHandler:
    def __init__(self, cfg, hw_id):
        self.cfg = cfg
        self.hw_id = hw_id
        self.out = None

    def _exec(self, packfile):
        proc = subprocess.Popen([self.cfg.homeworks[self.hw_id]["checker"], packfile],
                                stdin=utils.get_dev_null(), stdout=subprocess.PIPE)
        self.out = proc.communicate()[0]
        return proc.wait()

    @staticmethod
    def check_format(fname):
        return re.match(r'.*(\.tar\.gz|\.tgz|\.tar|\.tar.bz2|\.py)$', fname, flags=re.IGNORECASE)

    def handle(self, msg):
        archive = None
        for att in msg.attachments():
            if att.filename and MessageHandler.check_format(att.filename):
                archive = att
                break

        if archive is None:
            self.cfg.add_to_log('skip message (no appropriate attachment found)')
            return -1

        tf = tempfile.NamedTemporaryFile(suffix='_%s' % archive.filename, delete=True)
        tf.write(archive.content)
        tf.flush()
        rv = self._exec(tf.name)
        tf.close()

        return rv
