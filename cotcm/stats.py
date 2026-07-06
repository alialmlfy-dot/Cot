"""Tiny pure-Python stats helpers (no numpy — spec constraint). All operate on
plain lists of floats with explicit None handling."""


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def pstdev(xs):
    """Population standard deviation."""
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return (sum((x - m) ** 2 for x in xs) / n) ** 0.5


def median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def percentile(xs, p):
    """Linear-interpolation percentile (p in [0,100]), numpy 'linear' default."""
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    rank = (p / 100.0) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return s[lo] + (s[hi] - s[lo]) * frac


def pct_rank_leq(value, xs):
    """Causal percentile rank of `value` within xs: share of values <= value,
    as 0..100. xs must already be restricted to inception..t (no lookahead)."""
    if not xs:
        return None
    return 100.0 * sum(1 for x in xs if x <= value) / len(xs)
