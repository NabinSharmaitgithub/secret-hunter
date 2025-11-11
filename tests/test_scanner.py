import unittest
import os
import yaml
from secret_hunter.scanner import scan_file

class TestScanner(unittest.TestCase):

    def setUp(self):
        self.rules = {
            "rules": [
                {
                    "id": "test-key",
                    "regex": "TEST_KEY",
                    "type": "Test Key",
                    "confidence": "High"
                }
            ]
        }
        with open("test_rules.yml", "w") as f:
            yaml.dump(self.rules, f)

        with open("test_file.txt", "w") as f:
            f.write("This is a test file with a TEST_KEY.")

    def tearDown(self):
        os.remove("test_rules.yml")
        os.remove("test_file.txt")

    def test_scan_file(self):
        findings = scan_file("test_file.txt", self.rules["rules"])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["id"], "test-key")
        self.assertEqual(findings[0]["file"], "test_file.txt")
        self.assertEqual(findings[0]["line"], 1)
        self.assertEqual(findings[0]["snippet"], "This is a test file with a TEST_KEY.")
        self.assertEqual(findings[0]["type"], "Test Key")
        self.assertEqual(findings[0]["confidence"], "High")

if __name__ == '__main__':
    unittest.main()
