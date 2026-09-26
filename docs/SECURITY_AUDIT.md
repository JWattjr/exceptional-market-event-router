# Security review: Exceptional Market Event Router

Review date: 2026-09-26. Scope: `contracts/exceptional_market_event_router.py`, focused direct tests, and submission documentation. Review type: source-level engineering review; not formal verification, an independent audit, or a financial/legal guarantee.

## Controls in this source

| Area | Implemented behavior | Limit |
| --- | --- | --- |
| Frozen policy | Exact bounded fields, unique rule/source IDs, source-reference checks, allowed route validation, and a complete explicit route precedence with `NORMAL` last. SHA-256 binds market ID, policy, and source records. | The owner chooses the policy. A digest commits to configuration bytes; it does not prove the policy is sound or evidence truthful. |
| Assessment lifecycle | Starts `PENDING` / `UNRESOLVED`. Owner calls `begin_assessment`, which clears any previously active route and freezes the assessment time and expiry. `assess` must follow within that window. | If the assessment transaction fails to finalize, the finalized begin state remains `PENDING` / `UNRESOLVED`; callers must not act on a prior route. |
| Independent consensus | The leader and validator independently fetch and assess every source. The validator validates the leader candidate, reruns the analysis, and votes for agreement only on exact canonical equality of market/policy/time bindings, all source records, rule findings, citations, hashes, and reason code. | Network consensus determines whether enough validators agree. Direct-mode validator simulation is not a live multi-validator or StudioNet test. |
| Route derivation | Model output contains per-rule `TRIGGERED`, `NOT_TRIGGERED`, or `UNKNOWN` findings and citations; it cannot choose a route. Deterministic code derives `NORMAL` or the highest-priority triggered policy route. Codes are derived from frozen rule IDs. | The semantic finding is still model-mediated. Conflicting factual claims should be marked `UNKNOWN`; consensus cannot prove the model interpreted them correctly. |
| URL and body handling | Bounded HTTPS URLs, canonical host matching, DNS-name syntax checks, HTTP 200, strict UTF-8, per-source and aggregate byte limits. Transport exceptions become explicit unavailable evidence. Bodies exceeding the limits are rejected as truncated, never clipped. | URL checks do not prove DNS ownership, publisher identity, redirect destination safety, or factual authority. Network/redirect behavior depends on the GenLayer web runtime. |
| Freshness and citations | Every source must have a model-identified publication date no older than the frozen maximum age. Date-only values are treated as midnight UTC. Definite rules cite each required source with an exact bounded quotation present in that fetched body. | The date is extracted semantically and then checked deterministically; it is not signed metadata. A hash identifies fetched bytes but does not prove their truth. |
| Failure behavior | Missing, stale, undated, oversized, malformed, partially assessed, or citation-invalid evidence derives `UNRESOLVED`. A validator votes against a mismatching candidate. | A reverted/unfinalized assessment makes no state change. The separately finalized `begin_assessment` keeps the current state unresolved during that attempt. |
| History and access | Owner-only begin/assess; prior assessment records are retained up to 16. Further attempts are rejected at the cap instead of deleting old records. `get_state` exposes assessment time and expiry and returns an effective unresolved route after expiry. | The owner and downstream consumer remain responsible for operational monitoring and policy selection. |

## Prompt-injection and source risks

Evidence is explicitly framed as untrusted data and page instructions are not part of the contract policy. This does not guarantee semantic prompt-injection resistance. Mocked responses and direct tests cannot prove that a validator will ignore adversarial instructions in a live page. Production deployments should use carefully curated, narrow primary sources and independent operational review.

An exact quote and content hash bind a citation to bytes returned for the frozen URL during an assessment. They do not authenticate the publisher, establish factual truth, prove the source was not compromised, or prove the URL did not redirect. Source selection and interpretation remain material risks.

## Routing boundary

This contract only classifies a frozen policy and returns a route recommendation. It does not calculate prices, settle markets, pause liquidations, or invoke another protocol. Any consumer taking a consequential action must check the final GenLayer transaction status, wait for finality, verify the market ID and policy hash, and check that the assessment is still unexpired.

## Deployment evidence status

`deployments/studionet-release-2026-09-26-b.json` records the current StudioNet source commit and digest, bounded Federal Register evidence, finalized deployment and owner-gated assessment writes, validator votes, exact citation, and full state read-back. The assessment resolved `CLOSE_ONLY` with `FETCHED` / `CURRENT` evidence and reason `OK`. `deployments/studionet-release-2026-09-26.json` is retained as a `FAIL_CLOSED_DEMONSTRATION`: a CFTC fetch `HTTP_ERROR` produced `UNRESOLVED`. The older `deployments/studionet.json` and `deployments/bradbury.json` files remain `HISTORICAL_SOURCE_ONLY`.
