"""Tests for cotcm.http_client retry policy (requests is mocked; no network)."""

import unittest
from unittest import mock

from cotcm import http_client


class _Resp:
    def __init__(self, status, text="body"):
        self.status_code = status
        self.text = text


class TestGet(unittest.TestCase):
    def test_200_returns_immediately(self):
        with mock.patch.object(http_client.requests, "get",
                               return_value=_Resp(200)) as g:
            resp = http_client.get("https://x", retries=3)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(g.call_count, 1)

    def test_429_is_retried(self):
        seq = [_Resp(429), _Resp(429), _Resp(200)]
        with mock.patch.object(http_client.requests, "get", side_effect=seq) as g, \
             mock.patch.object(http_client.time, "sleep"):
            resp = http_client.get("https://x", retries=3)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(g.call_count, 3)

    def test_5xx_exhausts_retries_then_raises(self):
        with mock.patch.object(http_client.requests, "get",
                               return_value=_Resp(503)) as g, \
             mock.patch.object(http_client.time, "sleep"):
            with self.assertRaises(http_client.HttpError):
                http_client.get("https://x", retries=2)
            self.assertEqual(g.call_count, 3)

    def test_4xx_fails_loudly_without_retry(self):
        with mock.patch.object(http_client.requests, "get",
                               return_value=_Resp(400, "bad where clause")) as g, \
             mock.patch.object(http_client.time, "sleep"):
            with self.assertRaises(http_client.HttpError) as cm:
                http_client.get("https://x", retries=3)
            self.assertEqual(g.call_count, 1)
            self.assertIn("bad where clause", str(cm.exception))

    def test_connection_error_is_retried(self):
        import requests
        seq = [requests.ConnectionError("down"), _Resp(200)]
        with mock.patch.object(http_client.requests, "get", side_effect=seq), \
             mock.patch.object(http_client.time, "sleep"):
            resp = http_client.get("https://x", retries=1)
            self.assertEqual(resp.status_code, 200)


class TestGetCfg(unittest.TestCase):
    def test_app_token_header_added(self):
        cfg = {"http": {"timeout_s": 1, "retries": 0, "backoff_base_s": 0},
               "socrata": {"app_token": "tok123"}}
        with mock.patch.object(http_client.requests, "get",
                               return_value=_Resp(200)) as g:
            http_client.get_cfg(cfg, "https://x")
            self.assertEqual(g.call_args.kwargs["headers"]["X-App-Token"], "tok123")

    def test_no_token_no_header(self):
        cfg = {"http": {"timeout_s": 1, "retries": 0, "backoff_base_s": 0},
               "socrata": {"app_token": None}}
        with mock.patch.object(http_client.requests, "get",
                               return_value=_Resp(200)) as g:
            http_client.get_cfg(cfg, "https://x")
            self.assertNotIn("X-App-Token", g.call_args.kwargs["headers"])


if __name__ == "__main__":
    unittest.main()
