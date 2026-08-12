# Security and consensus audit: Exceptional Market Event Router

Audit date: 2026-08-12  
Scope: contracts/exceptional_market_event_router.py

## Result

No unresolved critical or high-severity source-level finding remains after the
hardening pass. This is an engineering audit, not formal verification and not
a financial or legal guarantee.

## Controls reviewed

| Area | Control |
| --- | --- |
| Consensus | Validators independently repeat the substantive evaluation and compare the decision-critical tuple. |
| Evidence | Evidence is bounded, HTTPS-only, and rejects localhost, internal domains, non-public IPv4 ranges, and userinfo URLs. |
| Prompt safety | Prompts instruct validators to treat fetched pages as untrusted data and ignore embedded instructions. |
| Failure mode | Source failure or ambiguity resolves to a conservative structured state rather than a payout or approval. |
| State | Inputs are snapshotted before non-deterministic closures; writes occur only after consensus returns. |
| Replay | Terminal or stateful methods preserve the most recent structured result and maintain attempt counters. |

## Residual risks

- Public webpages can change or become unavailable. Deployments should use
  pre-approved stable primary sources and an explicit freshness policy.
- Genuine semantic ambiguity can cause disagreement; that is preferable to a
  unilateral decision and should route to the documented fail-closed state.
- This primitive chooses a policy state; a downstream protocol must wait for
  GenLayer transaction finality before moving funds or applying an irreversible action.
