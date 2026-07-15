#!/usr/bin/env python3
"""Check the facts docs/02-project-plan.md restates from tables it also contains.

Every drift so far was a number in prose that no longer matched the table
beneath it: v1.1's "nine of the twelve" against an eleven-row register, and
its M1 of 2026-07-16 against its M2 of 2026-07-21. The tables are the
arithmetic; this asserts the prose still agrees with them.

v1.3 added two more, both found by review rather than by this script: the
module renumber left v1.2 numbers in §8.5 and §11, and three TBD deadlines
named the first day of the module they gate instead of the day before it.

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


def section(text, num):
    """The body of section `num`, up to the next heading of the same depth."""
    m = re.search(rf"^#+ {re.escape(num)} .*?$(.*?)(?=^#+ \d|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def module_names(text):
    """§6.1's build order: {number: name}. The one place module numbers are defined.

    Scoped to §6.1 -- every other numbered table in this document (§5.2's
    milestones, §11's questions) would otherwise answer to the same shape.
    """
    return {int(n): nm.strip().strip("*")
            for n, nm in re.findall(r"^\| (\d+) \| (.+?) \| ", section(text, "6.1"), re.M)}


def module_starts(text):
    """First working day of each module, from §6.3's week allocation.

    A week row names the day it ends, so week N spans working days 5N-4..5N.
    Entries inside a row run in order, so a module starts after whatever
    precedes it in the first week it appears.
    """
    starts = {}
    for wk, body in re.findall(r"^\| (\d+) \| \d{4}-\d{2}-\d{2} \| (.+?) \|\s*$", section(text, "6.3"), re.M):
        offset = 0.0
        for entry in body.split(";"):
            m = re.search(r"\bM(\d+)\b", entry)
            d = re.search(r"\((\d+(?:\.\d+)?)d", entry)
            if m and int(m.group(1)) not in starts:
                starts[int(m.group(1))] = 5 * (int(wk) - 1) + int(offset) + 1
            offset += float(d.group(1)) if d else 0.0
    return starts


def check_module_refs(text):
    """Every 'M<n> <Name>' in prose must name the module §6.1 numbers that way.

    The v1.3 renumber shifted eighteen modules by one and missed §8.5, §11
    question 6, and §2.4. Nothing else was checking.

    Passages naming a version state the number as it was then -- "M15 Payroll
    here is M14 Payroll at v1.2" is the point being made, not a stale ref --
    so anything scoped to v1.0 to v1.2 is left alone.
    """
    names = module_names(text)
    norm = {k: re.sub(r"\s*/\s*", "/", v) for k, v in names.items()}
    bad = []
    for para in re.split(r"\n|(?<=\.) ", text):
        if re.search(r"v1\.[0-2]", para):
            continue  # a version-scoped claim states the old number on purpose
        for n, said in set(re.findall(r"\bM(\d+) ([A-Z][A-Za-z/]*(?: [A-Z][A-Za-z/]*)?)", para)):
            real, cmp = names.get(int(n)), norm.get(int(n))
            if real is None or said.split()[0] not in cmp:
                hit = next((k for k, v in norm.items() if said.split()[0] in v), None)
                bad.append(f"  M{n} {said}: §6.1 has M{n} as {real or 'nothing'}"
                           + (f"; {said.split()[0]} is M{hit}" if hit else ""))
    return sorted(set(bad)) or None


def check_tbd_deadlines(text):
    """§8.1: a 'Before M<n> begins' deadline is the working day before it starts."""
    starts, bad = module_starts(text), []
    for n, iso in re.findall(r"Before M(\d+)[^,|]*begins, (\d{4}-\d{2}-\d{2})", text):
        start = starts.get(int(n))
        if start is None:
            continue
        want = workday(start - 1)
        if want.isoformat() != iso:
            bad.append(f"  §8.1 M{n}: deadline {iso}; M{n} begins working day "
                       f"{start} ({workday(start)}), so the day before is {want}")
    return bad or None


def selfcheck():
    assert workday(1) == START
    assert workday(5) == date(2026, 7, 21), "week 1 ends Tue 2026-07-21 per §6.2"
    assert workday(85) == date(2026, 11, 10), "the end date is working day 85"
    assert workday(81) == date(2026, 11, 4), "81 days of estimate land here"
    assert word("carries seventeen TBD items", r"carries (\w+) TBD items") == 17


if __name__ == "__main__":
    selfcheck()
    plan = (DOCS / "02-project-plan.md").read_text()
    fails = [line for check in (check_milestones, check_tbds, check_srs_version,
                           check_module_refs, check_tbd_deadlines)
             for line in (check(plan) or [])]
    print("\n".join(fails) if fails else "docs consistent")
    sys.exit(1 if fails else 0)
