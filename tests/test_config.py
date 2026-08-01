"""Tests for cotcm.config — path resolution and the env-var token override."""

import json
import os
import tempfile
import unittest
from unittest import mock

from cotcm import config


def _write_cfg(**over):
    cfg = {"db_path": "cot_cm.db", "reports_dir": "reports",
           "socrata": {"app_token": None}, "universe": []}
    cfg.update(over)
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(cfg, f)
    return path


class TestLoadConfig(unittest.TestCase):
    def test_relative_paths_resolve_against_repo_root(self):
        path = _write_cfg()
        try:
            cfg = config.load_config(path)
            self.assertTrue(os.path.isabs(cfg["db_path"]))
            self.assertTrue(cfg["db_path"].startswith(config.REPO_ROOT))
        finally:
            os.unlink(path)

    def test_env_token_overrides_file(self):
        path = _write_cfg()
        try:
            with mock.patch.dict(os.environ,
                                 {config.ENV_SOCRATA_TOKEN: "envtok"}):
                cfg = config.load_config(path)
            self.assertEqual(cfg["socrata"]["app_token"], "envtok")
        finally:
            os.unlink(path)

    def test_file_token_kept_without_env(self):
        path = _write_cfg(socrata={"app_token": "filetok"})
        try:
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop(config.ENV_SOCRATA_TOKEN, None)
                cfg = config.load_config(path)
            self.assertEqual(cfg["socrata"]["app_token"], "filetok")
        finally:
            os.unlink(path)


class TestEnabledUniverse(unittest.TestCase):
    def test_filter(self):
        cfg = {"universe": [{"root": "A", "enabled": True},
                            {"root": "B", "enabled": False},
                            {"root": "C"}]}
        roots = [u["root"] for u in config.enabled_universe(cfg)]
        self.assertEqual(roots, ["A"])


if __name__ == "__main__":
    unittest.main()
