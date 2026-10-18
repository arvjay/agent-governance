"""Typed models for the regulation -> control -> policy -> evidence chain."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Regulation(BaseModel):
    id: str
    citation: str
    title: str
    summary: str = ""


class Control(BaseModel):
    id: str
    title: str
    source_regulation: str
    agent: str
    resources: list[str] = []
    actions: list[str] = []
    coverage: Literal["full", "partial", "none"]


class Rule(BaseModel):
    name: str
    host: str
    methods: list[str] = ["*"]
    path: str  # exact path or fnmatch pattern, e.g. /v1/payroll*


class NetworkPolicies(BaseModel):
    allow: list[Rule] = []
    deny: list[Rule] = []


class Probe(BaseModel):
    method: str
    url: str


class PolicyTests(BaseModel):
    positive: list[Probe] = []
    negative: list[Probe] = []


class Policy(BaseModel):
    name: str
    version: str
    control_id: str
    agent: str
    mode: Literal["enforce", "audit"] = "enforce"
    network_policies: NetworkPolicies = NetworkPolicies()
    tests: PolicyTests = PolicyTests()


class Request(BaseModel):
    agent: str
    method: str
    url: str


class Decision(BaseModel):
    allowed: bool    # whether the request goes through
    violation: bool  # whether the request breaks the policy (true even in audit mode)
    rule: Optional[str] = None
    mode: Literal["enforce", "audit"]


class EvidenceRecord(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    regulation_id: str
    control_id: str
    policy_name: str
    policy_version: str
    request: Request
    decision: Decision


class AssuranceResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"
