"""Append traceable evidence records as JSON lines."""
from __future__ import annotations

from pathlib import Path

from .loader import ROOT
from .models import Control, Decision, EvidenceRecord, Policy, Regulation, Request

DEFAULT_LOG = ROOT / "evidence" / "evidence.jsonl"


def record(
    regulation: Regulation,
    control: Control,
    policy: Policy,
    request: Request,
    decision: Decision,
    log: Path = DEFAULT_LOG,
) -> EvidenceRecord:
    entry = EvidenceRecord(
        regulation_id=regulation.id,
        control_id=control.id,
        policy_name=policy.name,
        policy_version=policy.version,
        request=request,
        decision=decision,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(entry.model_dump_json() + "\n")
    return entry
