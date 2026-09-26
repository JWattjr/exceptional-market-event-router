# GenLayer Portal submission draft

**Contribution type:** Builder → Intelligent Contracts · **Title:** Exceptional Market Event Router
**Status:** Review candidate prepared locally. Do not present this source as deployed or submit the old deployment receipts as proof for it.

## Notes / Description

Exceptional Market Event Router classifies public evidence against a frozen, versioned policy. The owner finalizes `begin_assessment` first, clearing the previous route. Validators compare market/policy/time bindings, source hashes, rule findings, and exact citations. Code derives the route from triggered rules and frozen precedence; missing, stale, partial, invalid, or conflicting evidence returns `UNRESOLVED`. Assessments expire and retain up to 16 records. It does not set prices, settle markets, or execute downstream actions; consumers must verify transaction finality before acting. Includes 40 focused direct tests, lint/schema results, an audit, and a test matrix. Tests use mocks and do not prove live multi-validator behavior or prompt-injection resistance. The CFTC example is illustrative. Existing StudioNet and Bradbury receipts are historical only.

`begin_assessment` and `assess` are owner-gated so the market operator controls timing; every finalized assessment is appended to the public on-chain history, so re-running until a preferred route appears is visible to anyone. A reverted or unfinalized call cannot append contract state.

## Evidence links to publish after the source and documentation are committed

1. GitHub Repository — https://github.com/JWattjr/exceptional-market-event-router
2. GitHub File — https://github.com/JWattjr/exceptional-market-event-router/blob/main/contracts/exceptional_market_event_router.py
3. GitHub File — https://github.com/JWattjr/exceptional-market-event-router/blob/main/docs/SECURITY_AUDIT.md
4. GitHub File — https://github.com/JWattjr/exceptional-market-event-router/blob/main/docs/TEST_MATRIX.md
5. Authoritative evidence example — https://www.cftc.gov/PressRoom/PressReleases/9281-26

The source and documentation in this working copy have not been pushed, so the GitHub links above must not be represented as the hardened release until publication is verified. `deployments/studionet.json` and `deployments/bradbury.json` are historical records only.

## Exact submission blockers

- Commit and publish the reviewed source and documentation, then verify the public GitHub revision.
- Select the target network and deploy the published source. Record its Git commit and SHA-256 source digest with the actual deployment receipt; wait for `FINALIZED` and successful leader execution.
- Read `get_state` and verify the contract address, market ID, policy version/hash, and initial `PENDING` / `UNRESOLVED` state.
- Call `begin_assessment`, wait for finality, then call `assess` within its TTL. Wait for finality and record the actual consensus outcome and transaction receipt; do not imply unanimity unless every validator agreed.
- Read `get_state` again and record assessment time, expiry, route, reason, source hashes/citations, attempts, and history. Confirm the effective route is unresolved after expiry.
- Add the actual current Explorer contract URL and verified transaction links. The Portal's Explorer evidence slot is not ready for this source.
- Recheck the CFTC example against its frozen 60-day freshness limit if reusing it; its notice is stale for this example policy after 2026-10-10 UTC.
