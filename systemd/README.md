# systemd install (Raspberry Pi)

Two independent timers (spec section 7): the weekly ingest, and a separate
staleness guard so a silent ingest crash is still caught.

```bash
# 1. Edit User= and paths in the two .service files to match your deployment
#    (defaults assume user `pi` and repo at /home/pi/Cot).

# 2. Install units
sudo cp systemd/cot-*.service systemd/cot-*.timer /etc/systemd/system/
sudo systemctl daemon-reload

# 3. Enable + start the timers
sudo systemctl enable --now cot-weekly.timer cot-staleness.timer

# 4. Verify schedule
systemctl list-timers 'cot-*'
```

Schedules:
- **cot-weekly.timer** — Saturday 06:00 Asia/Riyadh, after the Friday 15:30 ET
  CFTC Disaggregated release. Runs `scripts/weekly_ingest.py`.
- **cot-staleness.timer** — Sunday 07:00 Asia/Riyadh. Runs
  `scripts/staleness_check.py`; alerts if the latest report_date is > 12 days old.

Inline `OnCalendar` timezones need systemd ≥ 252. On older Raspbian, remove
`Asia/Riyadh` from the timer files and instead run
`sudo timedatectl set-timezone Asia/Riyadh` (Riyadh has no DST).

Every run writes a row to the `heartbeat` table regardless of outcome. Inspect:

```bash
sqlite3 cot_cm.db \
  "SELECT run_ts, job, status, substr(message,1,60) FROM heartbeat ORDER BY id DESC LIMIT 10;"
journalctl -u cot-weekly.service -n 50
```
