import unittest
import os
from src.logger import Logger

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.test_log = "tests/test_base.log"
        self.logger = Logger(self.test_log)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def check_log_contains(self, message: str):
        with open(self.test_log, "r") as f:
            content = f.read()
        self.assertIn(message, content)
