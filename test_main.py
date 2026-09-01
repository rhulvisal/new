import unittest
import os
from fastapi.testclient import TestClient
from main import (
    app,
    extract_bkv,
    extract_rev,
    extract_dtsg,
    extract_lsd,
    calculate_jazoest,
    calculate_worker_count,
    parse_numbers_query,
    FacebookNumberChecker
)

class TestFacebookChecker(unittest.TestCase):

    def test_extract_bkv(self):
        html1 = '{"versioningID":"abc123xyz"}'
        self.assertEqual(extract_bkv(html1), "abc123xyz")

        html2 = 'WebBloksVersioningID="123456789012345678901234567890123456789012345"'
        self.assertEqual(extract_bkv(html2), "123456789012345678901234567890123456789012345")

    def test_extract_rev(self):
        html1 = '"client_revision":1009988'
        self.assertEqual(extract_rev(html1), "1009988")

        html2 = '"rev":1009989'
        self.assertEqual(extract_rev(html2), "1009989")

    def test_extract_dtsg(self):
        html1 = '"token":"NAf123456"'
        self.assertEqual(extract_dtsg(html1), "NAf123456:0:0")

        html2 = '"token":"NAf123456:0:0"'
        self.assertEqual(extract_dtsg(html2), "NAf123456:0:0")

        html3 = 'DTSGInitialData.*"token":"other_token"'
        self.assertEqual(extract_dtsg('DTSGInitialData{"token":"other_token"}'), "other_token")

    def test_extract_lsd(self):
        html1 = '"lsd":"LSD_TOKEN_123"'
        self.assertEqual(extract_lsd(html1), "LSD_TOKEN_123")

        html2 = '<input type="hidden" name="lsd" value="LSD_INPUT_VAL" />'
        self.assertEqual(extract_lsd(html2), "LSD_INPUT_VAL")

    def test_calculate_jazoest(self):
        self.assertEqual(calculate_jazoest("NAf123:0:0"), str(1 + 2 + 3 + 0 + 0 + 2))
        self.assertEqual(calculate_jazoest(""), "24821")

    def test_calculate_worker_count(self):
        self.assertEqual(calculate_worker_count(1.0), 3)
        self.assertEqual(calculate_worker_count(8.0), 24)
        self.assertEqual(calculate_worker_count(0.1), 1)

    def test_parse_numbers_query(self):
        self.assertEqual(parse_numbers_query("+123, +456; +789"), ["+123", "+456", "+789"])
        self.assertEqual(parse_numbers_query(""), [])

    def test_fastapi_endpoints(self):
        with TestClient(app) as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("service", response.json())

            response = client.get("/check?numbers=+123456")
            self.assertEqual(response.status_code, 200)
            self.assertIn("task_id", response.json())

    def test_facebook_number_checker_close(self):
        checker = FacebookNumberChecker(use_tor=False)
        self.assertTrue(hasattr(checker, 'close'))
        checker.close()

if __name__ == "__main__":
    unittest.main()
