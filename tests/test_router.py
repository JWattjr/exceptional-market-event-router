import json
def test_router_does_not_invent_price(direct_vm,direct_deploy):
    c=direct_deploy("contracts/exceptional_market_event_router.py","market",{"routes":["NORMAL"]},["https://example.org/status"])
    direct_vm.mock_web(r".*",{"status":200,"body":"normal operations"});direct_vm.mock_llm(r".*",json.dumps({"route":"NORMAL","event_codes":[]}))
    assert c.assess()["route"]=="NORMAL" and direct_vm.run_validator()
def test_router_outage_unresolved(direct_vm,direct_deploy):
    c=direct_deploy("contracts/exceptional_market_event_router.py","market",{"routes":["NORMAL"]},["https://example.org/status"]);direct_vm.mock_web(r".*",{"status":503,"body":""})
    assert c.assess()["route"]=="UNRESOLVED"
