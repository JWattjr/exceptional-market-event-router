import copy
import json
import sys
from pathlib import Path

import pytest


router = None


MARKET_ID = "perp:sample-market"
ASSESSMENT_TIME = "2026-09-26T00:00:00Z"
SOURCE = {"id": "primary", "url": "https://evidence.example.org/event", "host": "evidence.example.org"}
BODY = "Official notice: no emergency market event has been declared."


def _policy():
    return {
        "version": "router-v1",
        "allowed_routes": ["NORMAL", "CLOSE_ONLY", "PAUSE_LIQUIDATIONS", "FALLBACK_SETTLEMENT"],
        "route_precedence": ["FALLBACK_SETTLEMENT", "PAUSE_LIQUIDATIONS", "CLOSE_ONLY", "NORMAL"],
        "assessment_ttl_seconds": 3600,
        "max_evidence_age_seconds": 86400,
        "rules": [
            {
                "id": "emergency_notice",
                "route": "PAUSE_LIQUIDATIONS",
                "criteria": "The authority explicitly declares an emergency for this market.",
                "source_ids": ["primary"],
            }
        ],
    }


def _sources():
    return [copy.deepcopy(SOURCE)]


def _llm_result(policy=None, status="NOT_TRIGGERED", published_date="2026-09-26", quote=BODY):
    policy = policy or _policy()
    return {
        "source_observations": [
            {"source_id": source_id, "published_date": published_date}
            for source_id in [source["id"] for source in _sources()]
        ],
        "findings": [
            {
                "rule_id": rule["id"],
                "status": status,
                "citations": [] if status == "UNKNOWN" else [
                    {"source_id": source_id, "quote": quote, "locator": "Official notice"}
                    for source_id in rule["source_ids"]
                ],
            }
            for rule in policy["rules"]
        ],
    }


def _deploy(direct_deploy, policy=None, sources=None, market_id=MARKET_ID):
    contract = direct_deploy(
        "contracts/exceptional_market_event_router.py",
        market_id,
        policy or _policy(),
        sources or _sources(),
    )
    global router
    router = sys.modules["_contract_exceptional_market_event_router"]
    return contract


def _mock_success(direct_vm, policy=None, result=None, body=BODY):
    policy = policy or _policy()
    direct_vm.mock_web(r".*", {"status": 200, "body": body})
    direct_vm.mock_llm(r".*", json.dumps(result or _llm_result(policy)))
    direct_vm.warp(ASSESSMENT_TIME)


@pytest.fixture
def router_module(direct_deploy):
    _deploy(direct_deploy)
    return router


def _candidate(policy=None, market_id=MARKET_ID, assessment_time=ASSESSMENT_TIME):
    policy = policy or _policy()
    sources = _sources()
    config_hash = router._policy_hash(market_id, policy, sources)
    records = [
        {
            "source_id": "primary",
            "host": SOURCE["host"],
            "url": SOURCE["url"],
            "fetch_status": "FETCHED",
            "body_hash": "a" * 64,
            "published_date": "2026-09-26",
            "freshness": "CURRENT",
        }
    ]
    findings = [
        {
            "rule_id": rule["id"],
            "status": "NOT_TRIGGERED",
            "citations": [
                {"source_id": source_id, "quote": BODY, "locator": "Official notice"}
                for source_id in rule["source_ids"]
            ],
        }
        for rule in policy["rules"]
    ]
    candidate = router._candidate_shell(market_id, policy, config_hash, assessment_time, records, findings, "OK")
    return candidate, policy, sources, config_hash


def test_initial_state_is_pending_and_unresolved(direct_deploy):
    contract = _deploy(direct_deploy)

    state = contract.get_state()

    assert state["status"] == "PENDING"
    assert state["route"] == "UNRESOLVED"
    assert state["event_codes"] == []
    assert state["assessment_time"] == ""
    assert state["history"] == []


def test_owner_must_finalize_begin_before_nondeterministic_assessment(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm)

    with direct_vm.expect_revert("begin_assessment"):
        contract.assess()
    begun = contract.begin_assessment()
    assert begun["status"] == "PENDING"
    assert contract.get_state()["route"] == "UNRESOLVED"


def test_normal_decision_requires_and_binds_independent_assessment(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm)
    contract.begin_assessment()

    result = contract.assess()

    assert result["route"] == "NORMAL"
    assert result["assessment"]["market_id"] == MARKET_ID
    assert result["assessment"]["policy_hash"] == contract.get_state()["policy_hash"]
    assert result["assessment"]["assessment_time"] == ASSESSMENT_TIME
    assert direct_vm.run_validator()


def test_rule_routes_are_derived_and_route_must_be_policy_allowed(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm, result=_llm_result(status="TRIGGERED", quote="emergency market event"))
    contract.begin_assessment()

    result = contract.assess()

    assert result["route"] == "PAUSE_LIQUIDATIONS"
    assert result["event_codes"] == ["emergency_notice"]
    assert "route" not in result["assessment"]
    assert direct_vm.run_validator()


def test_explicit_precedence_resolves_conflicting_triggers(direct_vm, direct_deploy, direct_owner):
    policy = _policy()
    policy["rules"].append({
        "id": "regulatory_fallback",
        "route": "FALLBACK_SETTLEMENT",
        "criteria": "The regulator explicitly directs this market to stop and use a fallback.",
        "source_ids": ["primary"],
    })
    result = _llm_result(policy, status="TRIGGERED", quote="emergency market event")
    contract = _deploy(direct_deploy, policy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm, policy, result)
    contract.begin_assessment()

    resolved = contract.assess()

    assert resolved["route"] == "FALLBACK_SETTLEMENT"
    assert resolved["event_codes"] == ["emergency_notice", "regulatory_fallback"]
    assert direct_vm.run_validator()


@pytest.mark.parametrize("mutate", [
    lambda policy: policy.update(routes=[]),
    lambda policy: policy.update(allowed_routes=["NORMAL", "UNRESOLVED"]),
    lambda policy: policy.update(route_precedence=["NORMAL", "PAUSE_LIQUIDATIONS", "CLOSE_ONLY", "FALLBACK_SETTLEMENT"]),
    lambda policy: policy.update(rules=[]),
    lambda policy: policy["rules"].append(copy.deepcopy(policy["rules"][0])),
    lambda policy: policy["rules"][0].update(route="NORMAL"),
    lambda policy: policy["rules"][0].update(source_ids=["missing"]),
    lambda policy: policy["rules"][0].update(criteria=""),
    lambda policy: policy.update(unexpected=True),
])
def test_malformed_or_contradictory_policy_is_rejected(router_module, mutate):
    policy = _policy()
    mutate(policy)

    with pytest.raises(Exception):
        router._validate_policy(policy, _sources())


def test_a_rule_cannot_select_a_disallowed_route(router_module):
    policy = _policy()
    policy["allowed_routes"] = ["NORMAL", "PAUSE_LIQUIDATIONS"]
    policy["route_precedence"] = ["PAUSE_LIQUIDATIONS", "NORMAL"]
    policy["rules"][0]["route"] = "FALLBACK_SETTLEMENT"

    with pytest.raises(Exception):
        router._validate_policy(policy, _sources())


def test_duplicate_keys_in_constructor_json_are_rejected(router_module):
    duplicate_policy_json = '{"version":"one","version":"two"}'

    with pytest.raises(Exception):
        router._parse_json(duplicate_policy_json, "policy", router.MAX_POLICY_CHARS)


@pytest.mark.parametrize("url,host", [
    ("http://evidence.example.org/x", "evidence.example.org"),
    ("https://localhost/x", "localhost"),
    ("https://127.0.0.1/x", "127.0.0.1"),
    ("https://evidence.example.org:444/x", "evidence.example.org"),
    ("https://user@evidence.example.org/x", "evidence.example.org"),
])
def test_non_public_or_malformed_evidence_url_is_rejected(router_module, url, host):
    sources = [{"id": "primary", "url": url, "host": host}]

    with pytest.raises(Exception):
        router._validate_policy(_policy(), sources)


def test_wrong_market_candidate_is_rejected(router_module):
    candidate, policy, sources, config_hash = _candidate()
    candidate["market_id"] = "another-market"

    with pytest.raises(ValueError, match="different market"):
        router._validate_candidate(candidate, MARKET_ID, policy, sources, config_hash, ASSESSMENT_TIME)


@pytest.mark.parametrize("field,value", [
    ("policy_hash", "0" * 64),
    ("assessment_time", "2026-09-25T00:00:00Z"),
])
def test_wrong_policy_or_assessment_binding_is_rejected(router_module, field, value):
    candidate, policy, sources, config_hash = _candidate()
    candidate[field] = value

    with pytest.raises(ValueError, match="different market, policy, or assessment time"):
        router._validate_candidate(candidate, MARKET_ID, policy, sources, config_hash, ASSESSMENT_TIME)


def test_forged_leader_field_is_rejected(router_module):
    candidate, policy, sources, config_hash = _candidate()
    candidate["route"] = "FALLBACK_SETTLEMENT"

    with pytest.raises(ValueError, match="extra fields"):
        router._validate_candidate(candidate, MARKET_ID, policy, sources, config_hash, ASSESSMENT_TIME)


def test_unknown_or_fabricated_citation_fails_validation(router_module):
    policy = _policy()
    findings = _llm_result(policy)["findings"]
    findings[0]["citations"][0]["source_id"] = "unfrozen-source"

    assert not router._validate_citations(findings, policy["rules"], _sources(), {"primary": BODY})


def test_unverifiable_citation_leaves_route_unresolved(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    bad = _llm_result(status="TRIGGERED", quote="this text is not in the fetched page")
    _mock_success(direct_vm, result=bad)
    contract.begin_assessment()

    result = contract.assess()

    assert result["status"] == "UNRESOLVED"
    assert result["route"] == "UNRESOLVED"
    assert result["assessment"]["reason_code"] == "INVALID_CITATION"
    assert direct_vm.run_validator()


def test_partial_rule_findings_cannot_be_routed(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm, result=_llm_result(status="UNKNOWN"))
    contract.begin_assessment()

    result = contract.assess()

    assert result["route"] == "UNRESOLVED"
    assert result["assessment"]["reason_code"] == "PARTIAL_FINDINGS"
    assert direct_vm.run_validator()


def test_extra_model_fields_cannot_smuggle_a_route(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    forged = _llm_result()
    forged["route"] = "NORMAL"
    _mock_success(direct_vm, result=forged)
    contract.begin_assessment()

    result = contract.assess()

    assert result["route"] == "UNRESOLVED"
    assert result["assessment"]["reason_code"] == "INVALID_MODEL_RESULT"
    assert direct_vm.run_validator()


@pytest.mark.parametrize("published_date,expected", [
    ("2026-09-25", "NORMAL"),  # exactly 24 hours old at the assessment boundary
    ("2026-09-24", "UNRESOLVED"),
    ("2026-09-27", "UNRESOLVED"),
    ("", "UNRESOLVED"),
])
def test_evidence_freshness_boundary_is_enforced(direct_vm, direct_deploy, direct_owner, published_date, expected):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    result = _llm_result(published_date=published_date)
    _mock_success(direct_vm, result=result)
    contract.begin_assessment()

    resolved = contract.assess()

    assert resolved["route"] == expected
    assert direct_vm.run_validator()


def test_assessment_expiry_is_visible_and_fails_closed(direct_vm, direct_deploy, direct_owner):
    policy = _policy()
    policy["assessment_ttl_seconds"] = 60
    contract = _deploy(direct_deploy, policy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm, policy)
    contract.begin_assessment()
    contract.assess()

    direct_vm.warp("2026-09-26T00:01:00Z")
    assert contract.get_state()["status"] == "RESOLVED"
    direct_vm.warp("2026-09-26T00:01:01Z")
    state = contract.get_state()
    assert state["status"] == "EXPIRED"
    assert state["route"] == "UNRESOLVED"
    assert state["last_assessed_route"] == "NORMAL"


def test_http_error_is_recorded_as_unresolved(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    direct_vm.mock_web(r".*", {"status": 503, "body": "temporarily unavailable"})
    direct_vm.warp(ASSESSMENT_TIME)
    contract.begin_assessment()

    result = contract.assess()

    assert result["route"] == "UNRESOLVED"
    assert result["assessment"]["reason_code"] == "EVIDENCE_UNAVAILABLE"
    assert result["assessment"]["source_records"][0]["fetch_status"] == "HTTP_ERROR"
    assert direct_vm.run_validator()


def test_transport_exception_is_caught(router_module, monkeypatch):
    def fail(_url):
        raise OSError("synthetic transport failure")

    monkeypatch.setattr(router, "_request_source", fail)
    records, bodies = router._fetch_sources(_sources())

    assert records[0]["fetch_status"] == "TRANSPORT_ERROR"
    assert records[0]["body_hash"] == ""
    assert bodies == {}


def test_truncated_body_is_never_silently_classified(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    direct_vm.mock_web(r".*", {"status": 200, "body": "x" * (router.MAX_SOURCE_BYTES + 1)})
    direct_vm.warp(ASSESSMENT_TIME)
    contract.begin_assessment()

    result = contract.assess()

    assert result["route"] == "UNRESOLVED"
    assert result["assessment"]["source_records"][0]["fetch_status"] == "TRUNCATED"
    assert direct_vm.run_validator()


def test_only_owner_can_assess(direct_vm, direct_deploy, direct_owner, direct_bob):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm)
    contract.begin_assessment()
    contract.assess()
    direct_vm.run_validator()

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only owner"):
        contract.assess()


def test_reassessment_appends_distinct_records(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    _mock_success(direct_vm)
    contract.begin_assessment()
    contract.assess()
    assert direct_vm.run_validator()

    direct_vm.warp("2026-09-26T00:30:00Z")
    contract.begin_assessment()
    contract.assess()
    assert direct_vm.run_validator()
    history = contract.get_state()["history"]

    assert len(history) == 2
    assert history[0]["assessment"]["assessment_time"] == ASSESSMENT_TIME
    assert history[1]["assessment"]["assessment_time"] == "2026-09-26T00:30:00Z"


def test_hashes_bind_market_policy_and_sources(router_module):
    policy = _policy()
    first = router._policy_hash(MARKET_ID, policy, _sources())
    changed_policy = copy.deepcopy(policy)
    changed_policy["version"] = "router-v2"
    changed_sources = _sources()
    changed_sources[0]["url"] = "https://evidence.example.org/other"

    assert len(first) == 64
    assert first != router._policy_hash("different-market", policy, _sources())
    assert first != router._policy_hash(MARKET_ID, changed_policy, _sources())
    assert first != router._policy_hash(MARKET_ID, policy, changed_sources)
