# GenLayer Portal submission draft

**Contribution type:** Builder → Intelligent Contracts · **Title:** Exceptional Market Event Router
**Status:** Review candidate prepared locally. Do not present this source as deployed or submit the old deployment receipts as proof for it.

## Notes / Description

Exceptional Market Event Router derives bounded routes from public evidence against frozen market policies. Validators compare market/policy/time bindings, source hashes, findings, and citations; code applies frozen precedence. Incomplete, stale, conflicting, or unavailable evidence remains `UNRESOLVED`. `begin_assessment` and `assess` are owner-gated so the market operator controls timing; every finalized assessment is appended to the public on-chain history, so re-running until a preferred route appears is visible to anyone. StudioNet deployment and both writes finalized with leader `SUCCESS`. The single CFTC assessment returned `UNRESOLVED` / `EVIDENCE_UNAVAILABLE` (`HTTP_ERROR`, attempts=1); no successful CFTC classification is claimed, and no retry was made. Includes 40 mocked direct tests and lint; these do not prove live source success or injection resistance. It does not settle markets; consumers verify finality and expiry. StudioNet only; older records historical.

## Current release evidence — StudioNet only

1. GenLayer Explorer Contract — https://explorer-studio.genlayer.com/address/0x34870779543Aec41751B00FAaaE79FcB181dD679
2. Deployment transaction — https://explorer-studio.genlayer.com/tx/0x943af7acdd2cfe48312e0cfb6117451917847ee39418d71818c6725d28ac98b9
3. `begin_assessment` transaction — https://explorer-studio.genlayer.com/tx/0x68be03a7e2ab7bcf302c54a738ce6958ded23d860845f26d43459fe40416f3c4
4. `assess` transaction — https://explorer-studio.genlayer.com/tx/0x7370c5d3182df963ec1fc6aba50e626f89d7806f651d622662c3e17501e266a0
5. Current release manifest — https://github.com/JWattjr/exceptional-market-event-router/blob/main/deployments/studionet-release-2026-09-26.json
6. Pinned contract source (commit `7716a9e5772b70e9f7cbe7576425485f4c3c05ef`) — https://github.com/JWattjr/exceptional-market-event-router/blob/7716a9e5772b70e9f7cbe7576425485f4c3c05ef/contracts/exceptional_market_event_router.py
7. GitHub Repository — https://github.com/JWattjr/exceptional-market-event-router
8. Security review — https://github.com/JWattjr/exceptional-market-event-router/blob/7716a9e5772b70e9f7cbe7576425485f4c3c05ef/docs/SECURITY_AUDIT.md
9. Test matrix — https://github.com/JWattjr/exceptional-market-event-router/blob/7716a9e5772b70e9f7cbe7576425485f4c3c05ef/docs/TEST_MATRIX.md
10. Authoritative evidence example — https://www.cftc.gov/PressRoom/PressReleases/9281-26

The pinned contract source and Explorer contract/transaction links returned HTTP 200 in read-only checks. The current release manifest and documentation are recorded in the evidence commit. `deployments/studionet.json` and `deployments/bradbury.json` remain historical only.

## Live limitation

The live CFTC assessment did not resolve because the GenLayer web fetch returned `HTTP_ERROR`. The conservative `UNRESOLVED` result is recorded without retrying. This proves the fail-closed unavailable-evidence path on StudioNet, not a successful public-source classification or prompt-injection resistance.
