import unittest
from src.logger import Logger, main
from tests.base import BaseTest
import os

class TestLogger(BaseTest):
    def test_log_writes_file(self):
        self.logger.log("Test message")
        with open(self.test_log, "r") as f:
            content = f.read()
        self.assertIn("Test message", content)

    def test_logger_multiple_logs(self):
        self.logger.log("Msg 1")
        self.logger.log("Msg 2")
        with open(self.test_log, "r") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("Msg 1", lines[0])
        self.assertIn("Msg 2", lines[1])

    def test_main(self):
        import os
        # We need to ensure the directory exists for main() to run without error
        # But main() also does os.makedirs("logs", exist_ok=True)
        # This test might be tricky because it affects the filesystem.
        # Let's just test that main doesn't crash.
        try:
            main()
        except Exception as e:
            self.fail(f"main() raised {type(e).__name__} unexpectedly!")

if __name__ == '__main__':
    unittest.main()
