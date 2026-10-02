import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import preflight


def config():
    return {"frame_account_id": "account-1", "max_file_bytes": 100, "reserve_bytes": 20,
            "routes": [{"drive_folder_id": "source-1", "frame_folder_id": "target-1"}]}


class PreflightTests(unittest.TestCase):
    def test_template_ids_are_rejected_before_network_access(self):
        c = config()
        c["frame_account_id"] = "REPLACE_FRAME_ACCOUNT_ID"
        with patch("preflight.get_json") as api:
            with self.assertRaises(ValueError):
                preflight.inspect(c)
            api.assert_not_called()

    def test_ambiguous_folder_mapping_is_rejected(self):
        c = config()
        c["routes"].append({"drive_folder_id": "source-1", "frame_folder_id": "other-target"})
        with self.assertRaises(ValueError):
            preflight.validate(c)

    def test_offline_checks_do_not_read_tokens_or_call_apis(self):
        with patch("preflight.get_json") as api, patch.dict(os.environ, {}, clear=True):
            result = preflight.inspect(config(), offline=True)
        api.assert_not_called()
        self.assertTrue(result["offline"])
        self.assertIn("cloud_schedule", result["not_tested"])

    def test_tokens_and_response_body_are_not_disclosed_on_http_error(self):
        secret = "sensitive-test-token"
        with patch("preflight.build_opener") as opener:
            opener.return_value.open.side_effect = HTTPError("https://api.frame.io/", 401, secret, {}, None)
            with self.assertRaises(RuntimeError) as error:
                preflight.get_json("https://api.frame.io/v4/accounts", secret)
        self.assertEqual(str(error.exception), "API returned HTTP 401")
        self.assertNotIn(secret, str(error.exception))

    def test_api_redirection_is_disabled(self):
        self.assertIsNone(preflight.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.test"))

    def test_unapproved_api_host_is_rejected(self):
        with self.assertRaises(ValueError):
            preflight.get_json("https://api.frame.io.evil.test/", "token")

    def test_missing_credentials_stop_before_network_access(self):
        with patch.dict(os.environ, {}, clear=True), patch("preflight.get_json") as api:
            with self.assertRaises(ValueError):
                preflight.inspect(config())
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
