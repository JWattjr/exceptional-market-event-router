# GenLayer Portal submission draft

**Contribution type:** Builder → Intelligent Contracts · **Title:** Exceptional Market Event Router
**Status:** Current source deployed and resolved on StudioNet. No Bradbury evidence is claimed.

## Notes / Description

Exceptional Market Event Router derives bounded routes from public evidence against frozen market policies. Its current StudioNet run resolved `CLOSE_ONLY` from a 798-byte official Federal Register JSON record of an SEC order approving temporary overnight price-band protections for extraordinary market volatility. Evidence was `FETCHED` / `CURRENT`; the frozen rule was `TRIGGERED` with an exact title citation and attempts=1. Deployment, `begin_assessment`, and `assess` finalized with leader `SUCCESS`; the assessment recorded 3 `AGREE` and 2 `IDLE` votes. Owner-gated timing and retained history make finalized reruns visible. The earlier CFTC run is preserved as fail-closed evidence: `HTTP_ERROR` produced `UNRESOLVED`, not a normal route. Includes 40 focused direct tests and lint. Tests do not prove prompt-injection resistance. It routes only; consumers verify finality and expiry. StudioNet only.

## Current release evidence — StudioNet only

1. GenLayer Explorer Contract — https://explorer-studio.genlayer.com/address/0xDE6c9A4f2E7EfdF9dCc7b94640Ca07B1A42f766F
2. Deployment transaction — https://explorer-studio.genlayer.com/tx/0x6d3f0167e21756f23e86ffe409e7a6e20f1756a2d1d18378cc6acf3b058039ad
3. `begin_assessment` transaction — https://explorer-studio.genlayer.com/tx/0xd970144b1ed1790c94d981c2c921290cd40e96f3290abff4fe106581c10063ee
4. `assess` transaction — https://explorer-studio.genlayer.com/tx/0xa06bad86d4ad54bcddfde4d0a7e684cf3651f980ea141944b3077d7379c13581
5. Current successful release manifest — https://github.com/JWattjr/exceptional-market-event-router/blob/main/deployments/studionet-release-2026-09-26-b.json
6. Pinned deployed contract source (commit `20c3f7963f49b264ad9dda1183709b228339dff7`) — https://github.com/JWattjr/exceptional-market-event-router/blob/20c3f7963f49b264ad9dda1183709b228339dff7/contracts/exceptional_market_event_router.py
7. GitHub Repository — https://github.com/JWattjr/exceptional-market-event-router
8. Official evidence — https://www.federalregister.gov/api/v1/documents/2026-16201.json?fields%5B%5D=document_number&fields%5B%5D=title&fields%5B%5D=publication_date&fields%5B%5D=agencies&fields%5B%5D=html_url
9. Security review — https://github.com/JWattjr/exceptional-market-event-router/blob/main/docs/SECURITY_AUDIT.md
10. Test matrix — https://github.com/JWattjr/exceptional-market-event-router/blob/main/docs/TEST_MATRIX.md
11. Earlier fail-closed demonstration — https://github.com/JWattjr/exceptional-market-event-router/blob/main/deployments/studionet-release-2026-09-26.json

The deployed source remained byte-identical to the pinned Git blob. The current successful manifest contains the constructor arguments, source hash, validator votes, exact citation, and full state read-back. The earlier CFTC manifest is labeled `FAIL_CLOSED_DEMONSTRATION`; `deployments/studionet.json` and `deployments/bradbury.json` remain historical only.

## Evidence boundary

The successful run demonstrates one source-backed, cited classification and the earlier run demonstrates fail-closed handling when evidence is unavailable. Neither proves the source is true, that all future validator sets agree, or that prompt-injection resistance is guaranteed.
