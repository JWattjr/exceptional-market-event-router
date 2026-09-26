# Test matrix: Exceptional Market Event Router

Last local run: 2026-09-26 · Command: `python -m pytest tests -q` · Result: **40 passed** (GenLayer direct-mode runner with mocked web/LLM results and deterministic helper checks).

These tests do not establish behavior against live public webpages or agreement among StudioNet/Bradbury validators. Some direct tests invoke the test runner's validator callback with mocked outputs; this is not a live network consensus test. All examples in test fixtures are synthetic except the separately documented CFTC URL example, which is not fetched by this suite.

## Focused cases

| Test coverage | Expected behavior | Test type |
| --- | --- | --- |
| Initial state; begin-before-assess | Start `PENDING` / `UNRESOLVED`; finalized begin clears an older active route and binds assessment time/expiry. | Direct mode |
| Malformed and contradictory policy inputs | Reject empty rules, unsupported/disallowed routes, incomplete or wrongly ordered precedence, duplicate IDs, unknown source references, blank criteria, and extra fields. | Direct helper validation |
| URL/source shape | Reject non-HTTPS, localhost, IP literal, userinfo, nonstandard port, and mismatched host identity. | Direct helper validation |
| Market/policy binding | Reject a candidate with the wrong market ID; config commitment changes with market, version, policy, or source changes. | Direct helper validation |
| Forged fields and citations | Reject candidate extra keys, unknown source references, and quotations that do not occur in the fetched body. | Direct helper and direct mode |
| Route derivation | Rule vector cannot supply a route; deterministic priority selects among multiple triggered routes; codes come from triggered frozen rule IDs. | Direct mode with validator callback |
| Partial findings | Any `UNKNOWN` rule leaves the assessment `UNRESOLVED`. | Direct mode with validator callback |
| Evidence age | Exact 24-hour boundary is current; older, future-dated, or missing dates stay unresolved. | Direct mode with validator callback |
| Assessment expiry | Route remains usable at the exact TTL boundary and becomes effectively `EXPIRED` / `UNRESOLVED` after it. | Direct mode |
| Fetch failures | HTTP error and mocked transport exception produce explicit unavailable results, never a fresh `NORMAL`. | Direct mode and helper check |
| Oversized body | Body beyond configured byte limit is marked `TRUNCATED`; no prefix is classified. | Direct mode with validator callback |
| Authorization and history | Only owner can assess; reassessments append distinct records instead of replacing prior entries. | Direct mode |

## Contract checks

| Command | Result |
| --- | --- |
| `python -m genvm_linter.cli check contracts/exceptional_market_event_router.py --json` | Passed: 3 AST lint checks and SDK semantic validation. Linter emitted an informational warning that a newer runner hash exists; network access prevented resolving its release metadata. The source remains pinned to the documented runner hash. |
| `python -m genvm_linter.cli schema contracts/exceptional_market_event_router.py --json` | Passed: 3 constructor string parameters; `begin_assessment` and `assess` write methods; `get_state` view method. |
| `python -m pytest tests -q` | Passed: 40 tests. |
| `python -m genvm_linter.cli typecheck contracts/exceptional_market_event_router.py --json` | Attempted but unavailable: `pyright` is not installed. No typecheck pass is claimed. |

No full integration test or Portal submission was performed. A separate one-time StudioNet deployment and live assessment is recorded in `deployments/studionet-release-2026-09-26.json`: all three transactions finalized with leader `SUCCESS`, while the assessment remained `UNRESOLVED` because the GenLayer web fetch returned `HTTP_ERROR`. This live attempt is not a substitute for the mocked test suite and does not demonstrate a successful source-backed classification.
