"""Command-line entry point: check a single request, or run assurance for a policy."""
from __future__ import annotations

import argparse

from . import assurance, enforcer, evidence
from .loader import load_chain
from .models import Request


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_governance")
    parser.add_argument("--policy", default="hr_leave_balance_only")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="evaluate one agent request")
    check.add_argument("method")
    check.add_argument("url")
    check.add_argument("--agent", required=True)

    assure = sub.add_parser("assure", help="run the policy's tests and report assurance")
    assure.add_argument("--downstream-consistent", choices=["yes", "no"])

    args = parser.parse_args(argv)
    regulation, control, policy = load_chain(args.policy)

    if args.command == "check":
        request = Request(agent=args.agent, method=args.method, url=args.url)
        decision = enforcer.evaluate(policy, request)
        evidence.record(regulation, control, policy, request, decision)
        verdict = "ALLOW" if decision.allowed else "DENY"
        print(f"{verdict} (violation={decision.violation}, rule={decision.rule}, mode={decision.mode})")
        return 0 if decision.allowed else 1

    run = lambda cases: [
        enforcer.evaluate(policy, Request(agent=policy.agent, method=c.method, url=c.url)) for c in cases
    ]
    downstream = None if args.downstream_consistent is None else args.downstream_consistent == "yes"
    results = assurance.assess(policy, policy, run(policy.tests.positive), run(policy.tests.negative), downstream)
    print(f"{regulation.citation} -> {control.id} -> {policy.name}@{policy.version}")
    for question, result in results.items():
        print(f"  {question:28} {result.value}")
    return 0 if results["overall"] is assurance.R.PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
