"""Load YAML definitions and resolve regulation -> control -> policy links."""
from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from .models import Control, Policy, Regulation

ROOT = Path(__file__).resolve().parents[2]
M = TypeVar("M", bound=BaseModel)


def load(path: Path, model: type[M]) -> M:
    return model.model_validate(yaml.safe_load(path.read_text()))


def load_all(directory: Path, model: type[M]) -> list[M]:
    return [load(p, model) for p in sorted(directory.glob("*.yaml"))]


def load_chain(policy_name: str, root: Path = ROOT) -> tuple[Regulation, Control, Policy]:
    """Return the regulation and control that a policy traces back to."""
    policy = load(root / "policies" / f"{policy_name}.yaml", Policy)
    control = next(c for c in load_all(root / "controls", Control) if c.id == policy.control_id)
    regulation = next(
        r for r in load_all(root / "regulations", Regulation) if r.id == control.source_regulation
    )
    return regulation, control, policy
