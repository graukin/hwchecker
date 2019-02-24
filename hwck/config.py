import ConfigParser
import json


class HwckConfig:
    def __init__(self, path):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(path)

        self.check_interval = self.config.getint('checker', 'check_interval')
        self.max_fails = self.config.getint('checker', 'check_interval')

        self.imap_server = self.config.get('servers', 'imap_server')
        self.smtp_server = self.config.get('servers', 'smtp_server')

        self.username = self.config.get('credentials', 'user')
        self._read_password()

        self.homeworks = json.loads(self.config.get('checker', 'homeworks'))

        self.src_folder = None
        self.ok_folder = None
        self.err_folder = None
        self.addr = None

    def _read_password(self):
        try:
            path = self.config.get('credentials', 'password_file')
        except ConfigParser.NoOptionError:
            pass
        else:
            with open(path, 'r') as f:
                line = f.readline()
                self.password = line.strip()

    def create_folders(self, hw_id):
        list_id = hw_id % len(self.homeworks)
        self.src_folder = "{}_infosearch@mail.ru".format(self.homeworks[list_id])
        self.ok_folder = "{}/success".format(self.src_folder)
        self.err_folder = "{}/fail".format(self.src_folder)
        self.addr = self.src_folder
