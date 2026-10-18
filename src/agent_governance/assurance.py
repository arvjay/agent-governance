"""Answer the four assurance questions. Missing evidence is UNRESOLVED, never an assumed pass."""
from __future__ import annotations

from .models import AssuranceResult, Decision, Policy

R = AssuranceResult


def _check(evidence: list | None, ok) -> AssuranceResult:
    if not evidence:
        return R.UNRESOLVED
    return R.PASS if all(ok(e) for e in evidence) else R.FAIL


def assess(
    expected: Policy,
    deployed: Policy | None,
    positive: list[Decision] | None,
    negative: list[Decision] | None,
    downstream_consistent: bool | None,
) -> dict[str, AssuranceResult]:
    if deployed is None:
        correct_policy = R.UNRESOLVED
    else:
        same = (deployed.name, deployed.version, deployed.agent, deployed.mode) == (
            expected.name, expected.version, expected.agent, expected.mode,
        )
        correct_policy = R.PASS if same else R.FAIL

    results = {
        "correct_policy_deployed": correct_policy,
        "permitted_activity_works": _check(positive, lambda d: d.allowed),
        "prohibited_actions_stopped": _check(negative, lambda d: not d.allowed),
        "downstream_consistent": (
            R.UNRESOLVED if downstream_consistent is None else R.PASS if downstream_consistent else R.FAIL
        ),
    }
    values = results.values()
    results["overall"] = R.FAIL if R.FAIL in values else R.UNRESOLVED if R.UNRESOLVED in values else R.PASS
    return results
