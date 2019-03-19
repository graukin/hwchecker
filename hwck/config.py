import ConfigParser
import json
import logging

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('hwchecker')


class HwckConfig:
    def __init__(self, path):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(path)

        self.check_interval = self.config.getint('checker', 'check_interval')
        self.max_fails = self.config.getint('checker', 'max_fails')
        self.max_attempts = self.config.getint('checker', 'max_attempts')

        self.imap_server = self.config.get('servers', 'imap_server')
        self.smtp_server = self.config.get('servers', 'smtp_server')

        self.username = self.config.get('credentials', 'user')
        self._read_password()

        self.homeworks = json.loads(self.config.get('checker', 'homeworks'))
        self._read_students()

        self.src_folder = None
        self.ok_folder = None
        self.err_folder = None
        self.addr = None

        self.add_to_log("Config loaded")

    def _read_password(self):
        try:
            path = self.config.get('credentials', 'password_file')
        except ConfigParser.NoOptionError:
            pass
        else:
            with open(path, 'r') as f:
                line = f.readline()
                self.password = line.strip()
                
    def _read_students(self):
        try:
            path = self.config.get('checker', 'students_file')
        except ConfigParser.NoOptionError:
            pass
        else:
            with open(path, 'r') as f:
                line = f.readline()
                raw_students = json.loads(line.strip(), encoding="UTF8")
                self.students = {}
                for student in raw_students:
                    self.students[student["email"]] = {"name":student["name"],
                                                       "attempts":student["attempts"]}

    def check_mail(self, mail):
        self.add_to_log("Check mail: " + mail)
        if mail in self.students.keys():
            if self.students[mail]["attempts"] < self.max_attempts:
                self.students[mail]["attempts"] += 1
                return True
            else:
                self.add_to_log("Too many attempts for {}".format(mail))
        return False

    def get_allowed_mails(self):
        return self.students.keys()

    def add_to_log(self, msg):
        logger.info(msg=msg)

    def create_folders(self, hw_id):
        self.add_to_log("Create folders for " + hw_id)
        list_id = hw_id % len(self.homeworks)
        self.checker = silf.homeworks[list_id]["checker"]
        self.src_folder = "{}".format(self.homeworks[list_id]["mail"])
        self.ok_folder = "{}/success".format(self.src_folder)
        self.err_folder = "{}/fail".format(self.src_folder)
        self.bad_folder = "{}/bad".format(self.src_folder)
        self.addr = self.src_folder
