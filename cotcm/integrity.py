"""Per-ingest integrity checks (spec section 7). A violation must abort the
ingest with status='error' and NO partial commit — checks run on the parsed
in-memory batch BEFORE anything is written."""

# A single category's long or short leg cannot plausibly exceed total open
# interest. Small tolerance absorbs rounding in the published figures.
OI_TOLERANCE = 1.05

_CATEGORY_LEGS = [
    "prod_merc_long", "prod_merc_short", "swap_long", "swap_short",
    "mm_long", "mm_short", "other_rept_long", "other_rept_short",
    "nonrept_long", "nonrept_short",
]


class IntegrityError(Exception):
    pass


def check_batch(rows, min_contracts=5, expect_full_universe=True):
    """Validate a parsed batch of cot_raw row dicts.

    Returns (ok, violations). Rules:
      - >= min_contracts distinct contracts present (spec: >= 5)
      - open_interest > 0 for every row
      - each category leg within [0, OI * tolerance]
    `expect_full_universe` is True for the weekly snapshot (all contracts in one
    report date) and for backfill batches spanning full history; a caller doing
    a single-contract pull passes False to skip the breadth rule.
    """
    violations = []
    if not rows:
        return False, ["empty batch"]

    if expect_full_universe:
        n = len({r["cftc_code"] for r in rows})
        if n < min_contracts:
            violations.append(
                "only %d distinct contracts present (need >= %d)" % (n, min_contracts))

    for r in rows:
        tag = "%s@%s" % (r["cftc_code"], r["report_date"])
        oi = r.get("open_interest")
        if oi is None or oi <= 0:
            violations.append("%s: open_interest not > 0 (%r)" % (tag, oi))
            continue
        bound = oi * OI_TOLERANCE
        for leg in _CATEGORY_LEGS:
            v = r.get(leg)
            if v is None:
                continue
            if v < 0 or v > bound:
                violations.append(
                    "%s: %s=%.0f outside [0, %.0f] (OI=%.0f)" % (tag, leg, v, bound, oi))

    return (len(violations) == 0), violations


def assert_ok(rows, **kw):
    ok, violations = check_batch(rows, **kw)
    if not ok:
        raise IntegrityError("; ".join(violations[:20]))
    return True
