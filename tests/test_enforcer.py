import pytest

from agent_governance.enforcer import evaluate
from agent_governance.loader import load_chain
from agent_governance.models import Request

AGENT = "hr-leave-assistant"


@pytest.fixture
def policy():
    return load_chain("hr_leave_balance_only")[2]


def test_leave_balance_read_allowed(policy):
    d = evaluate(policy, Request(agent=AGENT, method="GET", url="https://hr.example/v1/me/leave-balance"))
    assert d.allowed and not d.violation and d.rule == "leave_balance_read"


@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "https://hr.example/v1/payroll"),
        ("GET", "https://hr.example/v1/medical/records"),
        ("PUT", "https://hr.example/v1/me/leave-balance"),
        ("GET", "https://other.example/v1/me/leave-balance"),
    ],
)
def test_prohibited_requests_denied(policy, method, url):
    d = evaluate(policy, Request(agent=AGENT, method=method, url=url))
    assert not d.allowed and d.violation


def test_other_agent_denied(policy):
    d = evaluate(policy, Request(agent="someone-else", method="GET", url="https://hr.example/v1/me/leave-balance"))
    assert not d.allowed


def test_audit_mode_records_but_allows(policy):
    audit = policy.model_copy(update={"mode": "audit"})
    d = evaluate(audit, Request(agent=AGENT, method="GET", url="https://hr.example/v1/payroll"))
    assert d.allowed and d.violation
