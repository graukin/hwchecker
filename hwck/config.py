import ConfigParser


class HwckConfig:
    def __init__(self, path):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(path)

        self.check_interval = self.config.getint('checker', 'check_interval')
        self.max_fails = self.config.getint('checker', 'check_interval')
        self.checker_exec = self.config.get('checker', 'exec')

        self.imap_server = self.config.get('servers', 'imap_server')
        self.smtp_server = self.config.get('servers', 'smtp_server')

        self.username = self.config.get('credentials', 'user')
        self._read_password()
        self.from_addr = self.config.get('credentials', 'from_addr')
        self.cc_addr = self.config.get('credentials', 'cc_addr')

        self.src_folder = self.config.get('folders', 'src_folder')
        self.ok_folder = self.config.get('folders', 'ok_folder')
        self.err_folder = self.config.get('folders', 'err_folder')

    def _read_password(self):
        try:
            path = self.config.get('credentials', 'password_file')
        except ConfigParser.NoOptionError:
            pass
        else:
            with open(path, 'r') as f:
                line = f.readline()
                self.password = line.strip()
