"""Evaluate agent requests against a network policy (default deny)."""
from __future__ import annotations

from fnmatch import fnmatch
from urllib.parse import urlparse

from .models import Decision, Policy, Request, Rule


def _matches(rule: Rule, method: str, host: str, path: str) -> bool:
    method_ok = "*" in rule.methods or method.upper() in (m.upper() for m in rule.methods)
    return method_ok and host == rule.host and fnmatch(path, rule.path)


def evaluate(policy: Policy, request: Request) -> Decision:
    url = urlparse(request.url)
    host, path = url.hostname or "", url.path or "/"

    matched: str | None = None
    violation = True
    if request.agent == policy.agent:
        deny = next((r for r in policy.network_policies.deny if _matches(r, request.method, host, path)), None)
        allow = next((r for r in policy.network_policies.allow if _matches(r, request.method, host, path)), None)
        if deny:
            matched = deny.name
        elif allow:
            matched, violation = allow.name, False

    # Audit mode records the violation but lets the request through.
    allowed = not violation or policy.mode == "audit"
    return Decision(allowed=allowed, violation=violation, rule=matched, mode=policy.mode)
