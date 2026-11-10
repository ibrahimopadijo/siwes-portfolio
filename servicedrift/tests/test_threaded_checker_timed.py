import csv
import os
import socket
import subprocess
import sys
import tempfile
import unittest

class TestThreadedCheckerCLI(unittest.TestCase):
    def test_open_local_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            port = server.getsockname()[1]
            with tempfile.TemporaryDirectory() as folder:
                report_path = os.path.join(folder, "test_report.csv")
                result = subprocess.run(
                        [
                            sys.executable,
                            "threaded_checker_timed.py",
                            "--ports",
                            str(port),
                            "--workers",
                            "1",
                            "--report",
                            report_path
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Port {port}: OPEN", result.stdout)
                with open(report_path, "r", newline="", encoding="utf-8") as file:
                    rows = list(csv.DictReader(file))

                self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["port"], str(port))
        self.assertEqual(rows[0]["status"], "OPEN")
        self.assertTrue(rows[0]["scan_started_at_utc"])
        self.assertTrue(rows[0]["scan_completed_at_utc"])

if __name__ == "main":
    unittest.main()
