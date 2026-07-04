"""Config loading. The universe and all sources are config-driven (v1.1 rule:
re-expanding the universe must be a config change, not a rewrite)."""

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(REPO_ROOT, "config.json")


def load_config(path=None):
    path = path or os.environ.get("COTCM_CONFIG", DEFAULT_CONFIG_PATH)
    with open(path, "r") as f:
        cfg = json.load(f)
    cfg["_config_path"] = path
    cfg["_repo_root"] = REPO_ROOT
    # Resolve relative paths against the repo root so cron/systemd cwd doesn't matter.
    if not os.path.isabs(cfg["db_path"]):
        cfg["db_path"] = os.path.join(REPO_ROOT, cfg["db_path"])
    if not os.path.isabs(cfg["reports_dir"]):
        cfg["reports_dir"] = os.path.join(REPO_ROOT, cfg["reports_dir"])
    return cfg


def enabled_universe(cfg):
    return [u for u in cfg["universe"] if u.get("enabled")]
