# Agent Governance

A minimal skeleton for turning regulatory requirements into enforceable runtime agent controls. It follows the chain from [Konfer's article](https://konfer.ai/resources/blog/regulatory-requirements-runtime-agent-controls/):

```
regulation -> scoped control -> executable policy (policy as code) -> tested behavior -> assurance evidence
```

The worked example is GDPR Art. 5(1)(c) (data minimisation). It maps to control `HR-DM-001` and policy `hr_leave_balance_only`, so the HR leave assistant may only call `GET /v1/me/leave-balance`.

## Layout

| Path | Purpose |
|---|---|
| `regulations/` | Source requirements |
| `controls/` | Scoped controls bound to an agent, resources and actions; runtime coverage is `full`, `partial` or `none` |
| `policies/` | Executable policies (`enforce` or `audit` mode, allow/deny network rules, positive/negative tests) |
| `src/agent_governance/` | Models, loader, enforcer, evidence log, assurance checks, CLI |
| `evidence/` | JSONL evidence linking regulation, control, policy version, agent and decision |
| `tests/` | Behavior tests |

## Usage

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q

export PYTHONPATH=src
python -m agent_governance.cli check GET https://hr.example/v1/me/leave-balance --agent hr-leave-assistant  # ALLOW
python -m agent_governance.cli check GET https://hr.example/v1/payroll --agent hr-leave-assistant           # DENY
python -m agent_governance.cli assure                               # downstream unknown -> UNRESOLVED
python -m agent_governance.cli assure --downstream-consistent yes    # PASS
```

Assurance answers four questions: was the correct policy deployed, does permitted activity work, are prohibited actions stopped, and does the downstream system match the decision. Missing evidence gives `UNRESOLVED`, never an assumed pass.
