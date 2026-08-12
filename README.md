# Exceptional Market Event Router

Classifies documented market disruption without acting as a price oracle.

## GenLayer-native decision

The contract makes the consensus-critical decision: **NORMAL, CLOSE_ONLY, PAUSE_LIQUIDATIONS, FALLBACK_SETTLEMENT, or UNRESOLVED**. It
freezes bounded inputs and approved public evidence sources. The leader and
validators independently fetch/evaluate that evidence and compare the compact
decision fields using a custom equivalence function. After consensus, the
calling protocol deterministically selects a precommitted perpetual-market safety route.

The contract fails closed when evidence is unavailable, ambiguous, or
validator consensus does not support the same substantive result. It does not
use a frontend answer, a single backend, or format-only validation.

## Verify

Run: python -m genvm_linter.cli lint contracts/exceptional_market_event_router.py --json
Run: python -m pytest tests -v

See docs/SECURITY_AUDIT.md, docs/TEST_MATRIX.md, and PORTAL_SUBMISSION.md.
