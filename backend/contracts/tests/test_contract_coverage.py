"""`docs/08-testing-plan.md` §3.2: the two-directional check that
`docs/06-api-contracts.md` and the served API agree. Reads the contract
document directly rather than a vendored copy, so the two cannot drift
independently of each other.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import get_resolver
from rest_framework.test import APIClient

# Endpoints that are real, working routes but are infrastructure rather
# than application API surface `docs/06-api-contracts.md` documents —
# named once here rather than causing a false "undocumented" failure.
# Paths are in the same normalized (no trailing slash) form _normalize()
# produces, not the raw URLconf/doc spelling.
NOT_APPLICATION_CONTRACT = {
    ('/api/health', frozenset({'GET'})),
    ('/api/schema', frozenset({'GET'})),
}

PARAM_RE = re.compile(r'\{[^}]+\}')
CONVERTER_RE = re.compile(r'<[^:>]+:([^>]+)>')


def _contracts_doc_path():
    for candidate in (settings.BASE_DIR / 'docs', settings.BASE_DIR.parent / 'docs'):
        path = candidate / '06-api-contracts.md'
        if path.exists():
            return path
    raise FileNotFoundError(
        "docs/06-api-contracts.md not found relative to BASE_DIR — "
        "is docs/ copied into this image? See backend/Dockerfile."
    )


def _normalize(path):
    """{id}, {doc_id}, <int:pk>, <str:report>, ... all become the same
    placeholder, so a path differing only in its parameter *name* between
    the doc and the URLconf still compares equal."""
    path = PARAM_RE.sub('{}', path)
    path = CONVERTER_RE.sub('{}', path)
    return path.rstrip('/')


def documented_endpoints():
    """Parses every `| `/api/...`  | METHOD[, METHOD...] |` row from
    docs/06-api-contracts.md §4. Returns {(normalized_path, method), ...}."""
    text = _contracts_doc_path().read_text()
    rows = re.findall(r"^\| `(/api/[^`]+)` \| ([A-Z, ]+) \|", text, re.MULTILINE)
    endpoints = set()
    for path, methods in rows:
        for method in methods.split(','):
            endpoints.add((_normalize(path), method.strip()))
    return endpoints


def served_endpoints():
    """Walks the live URLconf for every `/api/...` route this project
    itself registers, paired with the HTTP methods its view class actually
    implements (not just what DRF's default OPTIONS handler would allow)."""
    resolver = get_resolver()
    endpoints = set()
    client = APIClient()
    for pattern in _flatten(resolver.url_patterns):
        if not pattern.route.startswith('api/'):
            continue
        normalized = _normalize('/' + pattern.route)
        view = pattern.callback
        view_class = getattr(view, 'cls', None)
        if view_class is None:
            # A plain Django view (unexpected under /api/), not a DRF one.
            continue
        for method in ('get', 'post', 'patch', 'put', 'delete'):
            if hasattr(view_class, method):
                endpoints.add((normalized, method.upper()))
    return endpoints, client


def _flatten(url_patterns, prefix=''):
    for entry in url_patterns:
        route = prefix + str(entry.pattern)
        if hasattr(entry, 'url_patterns'):
            yield from _flatten(entry.url_patterns, route)
        else:
            entry.route = route
            yield entry


class ContractCoverageTests(TestCase):
    """§3.2's two-directional check, both directions live now that M18
    Testing has started (`docs/08-testing-plan.md` §3.2 — the
    no-undocumented-surface direction is one-directional only during
    development, both directions hold from here on)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.documented = documented_endpoints()
        cls.served, cls.client_probe = served_endpoints()

    def test_every_documented_endpoint_is_served(self):
        missing = self.documented - self.served
        self.assertEqual(
            missing, set(),
            f"docs/06-api-contracts.md documents these endpoints, but no view "
            f"in the URLconf implements them: {sorted(missing)}",
        )

    def test_no_undocumented_application_endpoint(self):
        undocumented = self.served - self.documented
        # Group by path so one path's several allowed methods aren't each
        # reported as if they were unrelated endpoints.
        by_path = {}
        for path, method in undocumented:
            if (path, frozenset({method})) in NOT_APPLICATION_CONTRACT:
                continue
            by_path.setdefault(path, set()).add(method)
        # A path is only a real gap if none of its methods are excused.
        offenders = {
            path: methods for path, methods in by_path.items()
            if not any((path, frozenset({m})) in NOT_APPLICATION_CONTRACT for m in methods)
        }
        self.assertEqual(
            offenders, {},
            f"These routes exist in the URLconf but are not documented in "
            f"docs/06-api-contracts.md §4: {offenders}. If this is genuinely "
            f"infrastructure rather than application API surface, add it to "
            f"NOT_APPLICATION_CONTRACT with a one-line reason instead of "
            f"silencing this test.",
        )

    def test_documented_endpoints_resolve_and_enforce_authentication(self):
        """A route existing in the URLconf (the two tests above) is not the
        same as it actually being reachable — this walks every documented
        (path, method) pair as a real unauthenticated request and asserts
        neither 404 (route doesn't resolve) nor 405 (method not allowed),
        without asserting the specific permission outcome, which is each
        module's own permission test suite's job (`docs/08-testing-plan.md`
        §3.1), not this contract-level check's."""
        placeholder_by_converter = {'int': '1', 'str': 'headcount'}
        failures = []
        for path, method in sorted(self.documented):
            concrete = path
            # {} placeholders in the normalized path all become '1' — every
            # documented {id}/{doc_id}/{job_id}-style parameter in this
            # project's URLconf is an <int:...> converter except the one
            # <str:report> case, substituted by name below instead.
            if 'reports/{}/export' in concrete:
                concrete = concrete.replace('{}', placeholder_by_converter['str'])
            concrete = concrete.replace('{}', placeholder_by_converter['int'])
            response = self.client_probe.generic(method, concrete + '/')
            if response.status_code in (404, 405):
                failures.append((path, method, response.status_code))
        self.assertEqual(
            failures, [],
            f"These documented endpoints returned 404/405 on a live request "
            f"(route missing or method not implemented at that URL): {failures}",
        )
