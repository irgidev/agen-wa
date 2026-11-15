"""Governance engine interface — the contract between track B and track C.

Track B (agent core) calls ``evaluate`` before executing any tool call, and
surfaces ``queue_approval`` verdicts to the user. Track C implements the
engine inside this package. The public signatures here are stable; track C
may add modules but must not change these names.
"""

from dataclasses import dataclass
from typing import Any, Protocol

VERDICT_ALLOW = "allow"
VERDICT_QUEUE_APPROVAL = "queue_approval"
VERDICT_DENY = "deny"


@dataclass(frozen=True)
class GovernanceDecision:
    verdict: str
    approval_id: str | None = None
    reason: str = ""


class GovernanceEngine(Protocol):
    def evaluate(self, user_wa_id: str, tool: str, args: dict[str, Any]) -> GovernanceDecision:
        """Decide whether a tool call may execute now, needs approval, or is denied."""
        ...

    def resolve(
        self, approval_id: str, approved: bool, operator_note: str = ""
    ) -> GovernanceDecision:
        """Apply an operator decision to a queued approval and notify the user."""
        ...

    def pending(self) -> list[dict[str, Any]]:
        """Return queued approvals for the operator console."""
        ...
