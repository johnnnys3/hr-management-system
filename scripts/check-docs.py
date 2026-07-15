#!/usr/bin/env python3
"""Check the three facts docs/02-project-plan.md restates from tables it also contains.

Every drift so far was a number in prose that no longer matched the table
beneath it: v1.1's "nine of the twelve" against an eleven-row register, and
its M1 of 2026-07-16 against its M2 of 2026-07-21. The tables are the
arithmetic; this asserts the prose still agrees with them.

Usage: python3 scripts/check-docs.py   (exit 1 on any mismatch)
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
START = date(2026, 7, 15)  # working day 1, a Wednesday. docs/02-project-plan.md §6.2

WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def workday(n):
    """Calendar date of working day n, counting START as 1. §6.2's rule, and its only implementation."""
    d, seen = START, 1
    while seen < n:
        d += timedelta(days=1)
        if d.weekday() < 5:  # ponytail: no holiday calendar -- §11 question 4 is open
            seen += 1
    return d


def word(text, pattern):
    """The number-word captured by pattern, as an int."""
    m = re.search(pattern, text, re.I)
    return WORDS.get(m.group(1).lower()) if m else None


def check_milestones(text):
    """§5.2: every 'Working day N' must resolve to the date its own row states."""
    bad = []
    for name, iso, n in re.findall(
        r"^\| (M\d+) \|[^|]*\| (\d{4}-\d{2}-\d{2})[^|]*\| Working day (\d+)", text, re.M
    ):
        want = workday(int(n))
        if want.isoformat() != iso:
            bad.append(f"  §5.2 {name}: states {iso}, working day {n} is {want}")
    return bad or None


def check_tbds(text):
    """§8.1/§8.2: the counts in prose must match the register's rows."""
    rows = re.findall(r"^\| (TBD-\d+) \| .*$", text, re.M)
    resolved = [r for r in re.findall(r"^\| (TBD-\d+) \| .*$", text, re.M)
                if re.search(rf"^\| {r} \|.*\*\*Resolved\*\*", text, re.M)]
    total, res, opn = len(rows), len(resolved), len(rows) - len(resolved)

    claims = [
        ("total", total, word(text, r"carries (\w+) TBD items")),
        ("resolved", res, word(text, r"(\w+) are resolved")),
        ("open", opn, word(text, r"\*\*(\w+) remain open")),
        ("open (§8.2)", opn, word(text, r"\*\*\w+ of the (\w+) open TBDs")),
    ]
    return [f"  §8 {label}: prose says {said}, register has {real}"
            for label, real, said in claims if said != real] or None


def check_srs_version(text):
    """The highest SRS version 02 cites must be the SRS's latest.

    Lower ones are history ("at v1.0 ...") and are left alone; a stale
    baseline shows up as the highest cited lagging the real one.
    """
    srs = (DOCS / "01-srs.md").read_text()
    latest = re.findall(r"\| ([\d]+\.[\d]+) \|\s*$", srs, re.M)[-1]
    cited = re.findall(r"`docs/01-srs\.md` v([\d.]+)", text)
    top = max(cited, key=lambda v: tuple(map(int, v.split("."))))
    if top != latest:
        return [f"  cites `docs/01-srs.md` v{top} at newest; SRS is at v{latest}"]
    return None


def selfcheck():
    assert workday(1) == START
    assert workday(5) == date(2026, 7, 21), "week 1 ends Tue 2026-07-21 per §6.2"
    assert workday(80) == date(2026, 11, 3), "the end date is working day 80"
    assert workday(78) == date(2026, 10, 30), "78 days of estimate land here"
    assert word("carries seventeen TBD items", r"carries (\w+) TBD items") == 17


if __name__ == "__main__":
    selfcheck()
    plan = (DOCS / "02-project-plan.md").read_text()
    fails = [line for check in (check_milestones, check_tbds, check_srs_version)
             for line in (check(plan) or [])]
    print("\n".join(fails) if fails else "docs consistent")
    sys.exit(1 if fails else 0)
