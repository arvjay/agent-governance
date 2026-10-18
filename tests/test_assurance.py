from agent_governance.assurance import R, assess
from agent_governance.loader import load_chain
from agent_governance.models import Decision

policy = load_chain("hr_leave_balance_only")[2]
ok = Decision(allowed=True, violation=False, mode="enforce")
blocked = Decision(allowed=False, violation=True, mode="enforce")
leaked = Decision(allowed=True, violation=True, mode="audit")


def test_all_evidence_passes():
    assert assess(policy, policy, [ok], [blocked], True)["overall"] is R.PASS


def test_missing_evidence_is_unresolved():
    results = assess(policy, policy, [ok], [blocked], None)
    assert results["downstream_consistent"] is R.UNRESOLVED
    assert results["overall"] is R.UNRESOLVED


def test_no_deployed_policy_is_unresolved():
    assert assess(policy, None, [ok], [blocked], True)["correct_policy_deployed"] is R.UNRESOLVED


def test_wrong_version_fails():
    deployed = policy.model_copy(update={"version": "0.9.0"})
    assert assess(policy, deployed, [ok], [blocked], True)["overall"] is R.FAIL


def test_prohibited_action_let_through_fails():
    assert assess(policy, policy, [ok], [leaked], True)["prohibited_actions_stopped"] is R.FAIL


def test_denied_but_downstream_changed_fails():
    assert assess(policy, policy, [ok], [blocked], False)["overall"] is R.FAIL
