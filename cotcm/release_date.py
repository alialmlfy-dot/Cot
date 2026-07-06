"""Release-date computation. Structural to the whole system (operating rule 3):
signals and backtests key off release_date, never report_date.

CFTC data are as-of Tuesday (report_date) and published the following Friday
(spec section 2: "the Friday >= 3 days after report_date"). Holiday weeks shift
the actual publication, so every computed release_date carries
release_date_estimated=1 until/unless a live publication calendar is wired in.
"""

from datetime import date, datetime, timedelta

FRIDAY = 4  # date.weekday(): Monday=0 ... Sunday=6


def parse_date(s):
    """Socrata dates arrive as 'YYYY-MM-DDT00:00:00.000' or 'YYYY-MM-DD'."""
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def release_date_for(report_date):
    """First Friday on/after report_date + 3 days.

    A Tuesday report -> the same week's Friday (Tue+3). Robust if report_date
    is ever not a Tuesday: advance to the next Friday at/after the +3-day floor.
    """
    if isinstance(report_date, str):
        report_date = parse_date(report_date)
    floor = report_date + timedelta(days=3)
    days_to_friday = (FRIDAY - floor.weekday()) % 7
    return floor + timedelta(days=days_to_friday)


def friday_of_week(d):
    """Friday of the ISO week containing d (used to align weekly price bars,
    which Yahoo labels by week-start, to the Friday close date)."""
    if isinstance(d, str):
        d = parse_date(d)
    return d + timedelta(days=(FRIDAY - d.weekday()))
