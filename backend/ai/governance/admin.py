from dataclasses import dataclass, field
from copy import deepcopy


class ChangeNotApproved(RuntimeError):
    pass


@dataclass
class ChangeRequest:
    change_id: str
    target_type: str
    target_id: str
    patch: dict
    status: str = "draft"
    approvals: list[int] = field(default_factory=list)

    def approve(self, operator_id: int) -> None:
        self.approvals.append(operator_id)
        self.status = "approved"


@dataclass(frozen=True)
class AppliedChange:
    status: str
    audit_log: dict


def _deep_merge(base: dict, patch: dict) -> dict:
    result = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def apply_change_request(change: ChangeRequest, *, before: dict) -> AppliedChange:
    if change.status != "approved":
        raise ChangeNotApproved(change.change_id)

    after = _deep_merge(before, change.patch)
    change.status = "applied"
    return AppliedChange(
        status=change.status,
        audit_log={
            "change_id": change.change_id,
            "target_type": change.target_type,
            "target_id": change.target_id,
            "before": before,
            "after": after,
            "approvals": list(change.approvals),
        },
    )
