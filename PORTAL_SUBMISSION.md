# GenLayer Portal submission

**Contribution type:** Builder â†’ Intelligent Contracts  
**Title:** Exceptional Market Event Router

## Notes / Description

Built an MIT-licensed, standalone Exceptional Market Event Router, a reusable GenLayer
Intelligent Contract that classifies documented market disruption without acting as a price oracle.. The constructor freezes
bounded policy inputs and public HTTPS evidence sources. The leader and
validators independently evaluate the same material through a custom
equivalence function that compares the substantive structured decisionâ€”
NORMAL, CLOSE_ONLY, PAUSE_LIQUIDATIONS, FALLBACK_SETTLEMENT, or UNRESOLVEDâ€”rather than merely validating output shape. The accepted
decision selects a precommitted perpetual-market safety route. Local/private evidence targets, malformed input,
source failure, ambiguity, model-output errors, unauthorized calls, and
validator disagreement fail closed. The repository includes pinned GenVM
source, direct consensus tests, a security audit, test matrix, and StudioNet /
Bradbury deployment manifests. It is a composable policy primitive and does
not custody funds or claim legal/financial authority.

## Evidence to add

1. GitHub Repository â€” https://github.com/JWattjr/exceptional-market-event-router
2. GitHub File â€” https://github.com/JWattjr/exceptional-market-event-router/blob/main/contracts/exceptional_market_event_router.py
3. GitHub File â€” https://github.com/JWattjr/exceptional-market-event-router/blob/main/docs/SECURITY_AUDIT.md
4. GitHub File â€” https://github.com/JWattjr/exceptional-market-event-router/blob/main/docs/TEST_MATRIX.md
5. GitHub File â€” https://github.com/JWattjr/exceptional-market-event-router/blob/main/deployments/studionet.json
6. GitHub File â€” https://github.com/JWattjr/exceptional-market-event-router/blob/main/deployments/bradbury.json
7. GenLayer Explorer Contract â€” add the final Bradbury address from deployments/bradbury.json
