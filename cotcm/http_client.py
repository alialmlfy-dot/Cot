"""HTTP with the ops-hardening rules from spec section 7:
30s timeout, retries with exponential backoff, then a loud failure
(exception propagates into the heartbeat wrapper).

Retry policy:
  - 429 (throttled) and 5xx are retried with backoff — Socrata rate-limits
    unauthenticated traffic, and one throttled page must not kill the
    weekly run.
  - Other 4xx are client errors: retrying cannot help, so fail loudly and
    immediately with a response-body excerpt instead of letting a confusing
    JSON decode error surface downstream.
"""

import time

import requests


class HttpError(Exception):
    pass


def get(url, params=None, headers=None, timeout_s=30, retries=3, backoff_base_s=2):
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout_s)
        except requests.RequestException as e:
            last_err = e
        else:
            if resp.status_code == 429 or resp.status_code >= 500:
                last_err = HttpError("HTTP %d from %s" % (resp.status_code, url))
            elif resp.status_code >= 400:
                raise HttpError("HTTP %d from %s: %s"
                                % (resp.status_code, url, resp.text[:200]))
            else:
                return resp
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
