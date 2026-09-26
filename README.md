# Exceptional Market Event Router

An owner-operated GenLayer primitive for classifying public evidence against a frozen market-event policy. It returns a bounded route label and evidence record; it does not set a settlement price, settle positions, or execute an action in another protocol.

## Decision and lifecycle

The constructor freezes one `market_id`, a versioned policy, and 1–6 public source identities. The policy defines allowed routes, a complete route-precedence order, rule IDs, trigger criteria, required sources, a maximum evidence age, and an assessment TTL. Its SHA-256 commitment binds the market ID, canonical policy, and canonical source list. That digest identifies the configuration bytes; it does not prove that the policy is wise or that a source is truthful.

The contract begins `PENDING` / `UNRESOLVED`. For each attempt, the owner first calls `begin_assessment` and waits for that write to finalize. This clears any previously active route and freezes the assessment start time and expiry. The owner then calls `assess` before that window expires. The leader and independent validators fetch each source, evaluate each frozen rule, and compare the complete canonical evidence/finding record. Every definite finding must include exact bounded quotations from each source required by its rule. Deterministic code chooses the route from triggered rules and the frozen precedence list. `NORMAL` is only selected when all sources are available, within the policy's date-age limit, and every rule has a definite finding. Missing, stale, undated, oversized, invalidly encoded, materially conflicting, partial, or inconsistent evidence remains `UNRESOLVED`; simultaneous definite triggers are handled by the explicit route precedence.

Each accepted assessment is bound to the market ID, policy version/hash, and the finalized `begin_assessment` block time. The record exposes its expiry. `get_state` reports `EXPIRED` / `UNRESOLVED` after the TTL, while retaining prior assessment records. If `assess` fails to finalize or its validators do not reach consensus, the already-finalized begin state remains `PENDING` / `UNRESOLVED`. History is capped at 16 assessments; further assessments are rejected rather than overwriting earlier records.

Only the deployer/owner can begin or perform an assessment. A consumer must wait for both the begin write and the assessment write to reach finality before taking a consequential action, and must independently check the returned route, policy hash, assessment time, and expiry. This contract does not call that consumer or guarantee transaction finality.

`begin_assessment` and `assess` are owner-gated so the market operator controls timing; every finalized assessment is appended to the public on-chain history, so re-running until a preferred route appears is visible to anyone. A reverted or unfinalized call cannot append contract state.

## Frozen policy shape

Pass `policy_json` and `sources_json` as JSON strings to the three-argument constructor. Fields are exact and bounded; unknown keys, duplicate IDs, inconsistent source references, unapproved route labels, or incomplete/conflicting precedence are rejected.

```json
{
  "version": "router-v1",
  "allowed_routes": ["NORMAL", "PAUSE_LIQUIDATIONS"],
  "route_precedence": ["PAUSE_LIQUIDATIONS", "NORMAL"],
  "assessment_ttl_seconds": 3600,
  "max_evidence_age_seconds": 5184000,
  "rules": [
    {
      "id": "cftc_emergency",
      "route": "PAUSE_LIQUIDATIONS",
      "criteria": "The CFTC release explicitly reports exercising emergency authority after the named venue notified it of a market emergency.",
      "source_ids": ["cftc-release-9281-26"]
    }
  ]
}
```

## Authoritative evidence example

The [CFTC release 9281-26](https://www.cftc.gov/PressRoom/PressReleases/9281-26) is a real official source dated 2026-08-11. As of 2026-09-26 it is within the example policy's 60-day evidence-age limit. The page says that the CFTC exercised emergency authority after KalshiEX notified it of a market emergency. It does not order a perpetual protocol to pause liquidations. Mapping that finding to `PAUSE_LIQUIDATIONS` is an illustrative deployer policy choice, not an action prescribed by the CFTC.

Example source argument:

```json
[
  {
    "id": "cftc-release-9281-26",
    "url": "https://www.cftc.gov/PressRoom/PressReleases/9281-26",
    "host": "www.cftc.gov"
  }
]
```

For this example, use market ID `venue:kalshiex:emergency-9281-26`, with the policy and source objects above serialized as the constructor's `policy_json` and `sources_json` string arguments. The example is scoped to review of the named venue-level emergency; it does not claim that the notice applies to unrelated markets.

A definite model finding must identify publication date `2026-08-11` and cite an exact bounded quote from the fetched page, such as the title “CFTC Exercises Emergency Authority to Ensure Market Stability”, with a locator such as “Release 9281-26 / title”. The contract checks that the quotation is present in that fetch, that the source ID is frozen in the rule, and that the source date is not future or older than the policy limit. The example is time-sensitive and should be refreshed before use if it has aged beyond 60 days.

## Evidence and limitations

- Source inputs require bounded HTTPS URLs, a syntactically valid DNS hostname, and a declared host equal to the URL host. The contract does not establish DNS ownership, publisher identity, safe redirects, or factual truth. Curators must select authoritative sources.
- The evidence body is accepted only if the HTTP status is 200, UTF-8 decoding succeeds, and the entire body fits the 12,000-byte per-source and 24,000-byte aggregate limits. It is never silently clipped. [GenLayer documents](https://docs.genlayer.com/developers/intelligent-contracts/examples/fetch-web-content) `web.get()` as returning plain text by default; a read-only text extraction of the CFTC page was 6,632 UTF-8 bytes including navigation and lookup metadata, below the per-source bound. This is a size check on the opened page text, not a measured GenVM response; no on-chain fetch was run.
- Publication dates are source-stated calendar dates and are treated as 00:00 UTC for conservative age checks. Missing or ambiguous dates fail closed. Assessment expiry is measured separately from the block timestamp.
- The SHA-256 value records the bytes fetched for an assessment; it does not prove those bytes are authentic or true.
- If independent source claims conflict on a rule, validators are instructed to return `UNKNOWN`; semantic detection of such conflicts is model-mediated and not guaranteed by deterministic code.
- Page instructions are presented to validators as untrusted evidence. Prompt wording and mocked tests do not guarantee semantic resistance to prompt injection.
- Local direct tests do not establish live network behavior, source availability, or agreement among public GenLayer validators. The current StudioNet deployment and one live assessment are recorded in [the release manifest](deployments/studionet-release-2026-09-26.json): deployment, `begin_assessment`, and `assess` finalized with successful leader execution, but the assessment remained `UNRESOLVED` because the GenLayer web fetch returned `HTTP_ERROR`. This does not demonstrate a successful CFTC classification. The older `deployments/studionet.json` and `deployments/bradbury.json` records remain historical only.

## Checks

```powershell
python -m genvm_linter.cli check contracts/exceptional_market_event_router.py --json
python -m genvm_linter.cli schema contracts/exceptional_market_event_router.py --json
python -m pytest tests -q
```

See [the security audit](docs/SECURITY_AUDIT.md), [the test matrix](docs/TEST_MATRIX.md), and [the Portal draft](PORTAL_SUBMISSION.md).
