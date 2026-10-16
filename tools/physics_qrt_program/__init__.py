"""Read-only Physics QRT low-thinking-agent evidence contracts.

This is a programme orchestration aid, not a scientific oracle, QRT authority,
permission service, or v3.6 lifecycle implementation.
"""
from .contracts import validate_lock, validate_receipt, converge

__all__ = ["validate_lock", "validate_receipt", "converge"]
