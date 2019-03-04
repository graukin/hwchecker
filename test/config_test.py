#! /usr/bin/env python

from hwck.config import HwckConfig
from unittest import TestCase


class ConfigTest(TestCase):
    def testFileLoad(self):
        config = HwckConfig("example.cfg")
        self.assertEqual(60, config.check_interval)
        self.assertEqual(5, config.max_fails)
        self.assertEqual(4, len(config.homeworks))
        self.assertTrue("sekitei1" in config.homeworks)
        self.assertEqual(5, len(config.students))
        self.assertTrue(config.check_mail("e3@mail.ru"))
        self.assertTrue(config.check_mail("e4@mail.ru"))
        self.assertFalse(config.check_mail("e4@mail.ru"))
        self.assertEqual("imap.mail.ru", config.imap_server)
        self.assertEqual(5, len(config.get_allowed_mails()))
