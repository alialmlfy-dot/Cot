"""HTTP with the ops-hardening rules from spec section 7:
30s timeout, 3 retries with exponential backoff, then a loud failure
(exception propagates into the heartbeat wrapper)."""

import time

import requests


class HttpError(Exception):
    pass


def get(url, params=None, headers=None, timeout_s=30, retries=3, backoff_base_s=2):
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout_s)
            if resp.status_code >= 500:
                raise HttpError("HTTP %d from %s" % (resp.status_code, url))
            return resp
        except (requests.RequestException, HttpError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_base_s * (2 ** attempt))
    raise HttpError("GET %s failed after %d attempts: %s" % (url, retries + 1, last_err))


def get_cfg(cfg, url, params=None, headers=None):
    http = cfg["http"]
    hdrs = dict(headers or {})
    token = cfg["socrata"].get("app_token")
    if token:
        hdrs["X-App-Token"] = token
    return get(
        url,
        params=params,
        headers=hdrs,
        timeout_s=http["timeout_s"],
        retries=http["retries"],
        backoff_base_s=http["backoff_base_s"],
    )
