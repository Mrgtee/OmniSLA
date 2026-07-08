import json
import pytest
from tests.direct.conftest import to_hex

CONTRACT_PATH = "contracts/OmniSLA.py"

def test_initialization(direct_vm, direct_deploy, direct_alice, direct_bob):
    # Deploy contract first so SDK is on sys.path
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    provider = to_hex(direct_alice)
    client = to_hex(direct_bob)
    
    details_str = contract.get_details()
    details = json.loads(details_str)
    
    assert details["provider"] == provider
    assert details["client"] == client
    assert details["target_url"] == "https://api.status.com"
    assert details["collateral_required"] == 1000
    assert details["premium_required"] == 500
    assert details["collateral_funded"] == 0
    assert details["premium_funded"] == 0
    assert details["validation_strategy"] == "contains"
    assert details["validation_rule"] == "healthy"
    assert details["max_allowed_violations"] == 2
    assert details["sla_end_time_iso"] == "2026-07-08T12:00:00Z"
    assert details["status"] == "Created"
    assert details["violations_count"] == 0

def test_deposit_and_activation(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # 1. Deposit collateral (from provider direct_alice)
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    details = json.loads(contract.get_details())
    assert details["collateral_funded"] == 1000
    assert details["status"] == "Created"
    
    # 2. Deposit premium (from client direct_bob)
    direct_vm.sender = direct_bob
    direct_vm.value = 500
    contract.deposit_premium()
    
    details = json.loads(contract.get_details())
    assert details["premium_funded"] == 500
    assert details["status"] == "Active"

def test_refund_before_active(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # Deposit collateral
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    details = json.loads(contract.get_details())
    assert details["collateral_funded"] == 1000
    
    # Refund collateral
    direct_vm.sender = direct_alice
    contract.refund()
    
    details = json.loads(contract.get_details())
    assert details["collateral_funded"] == 0

def test_check_sla_compliant_contains(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # Setup funding and activate
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    direct_vm.sender = direct_bob
    direct_vm.value = 500
    contract.deposit_premium()
    
    # Mock web response to be compliant
    direct_vm.mock_web("https://api.status.com", {"status": 200, "body": "system is healthy"})
    
    # Check SLA (requires Active status)
    direct_vm.sender = direct_alice
    res = contract.check_sla()
    
    assert res is True
    details = json.loads(contract.get_details())
    assert details["violations_count"] == 0
    assert details["status"] == "Active"

def test_check_sla_violating_contains(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # Setup funding and activate
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    direct_vm.sender = direct_bob
    direct_vm.value = 500
    contract.deposit_premium()
    
    # Mock web response to be violating (does not contain "healthy")
    direct_vm.mock_web("https://api.status.com", {"status": 200, "body": "system is critical"})
    
    direct_vm.sender = direct_alice
    
    # Violation 1
    res1 = contract.check_sla()
    assert res1 is False
    details = json.loads(contract.get_details())
    assert details["violations_count"] == 1
    assert details["status"] == "Active"
    
    # Violation 2 (reaches max_allowed_violations = 2)
    res2 = contract.check_sla()
    assert res2 is False
    details = json.loads(contract.get_details())
    assert details["violations_count"] == 2
    assert details["status"] == "Violated"

def test_check_sla_semantic_compliant(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "semantic",
        "response shows active status",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # Setup funding and activate
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    direct_vm.sender = direct_bob
    direct_vm.value = 500
    contract.deposit_premium()
    
    # Mock web response
    direct_vm.mock_web("https://api.status.com", {"status": 200, "body": '{"status": "active"}'})
    
    # Mock LLM evaluation
    direct_vm.mock_llm(r".*compliant.*", json.dumps({"compliant": True}))
    
    direct_vm.sender = direct_alice
    res = contract.check_sla()
    
    assert res is True
    details = json.loads(contract.get_details())
    assert details["violations_count"] == 0

def test_close_sla_expired(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # Setup funding and activate
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    direct_vm.sender = direct_bob
    direct_vm.value = 500
    contract.deposit_premium()
    
    # Warp time post expiry
    direct_vm.warp("2026-07-09T00:00:00Z")
    # Manually update genlayer.gl.message_raw datetime since vm.warp does not propagate it dynamically in tests
    import genlayer
    genlayer.gl.message_raw['datetime'] = "2026-07-09T00:00:00Z"
    
    # Close SLA
    direct_vm.sender = direct_alice
    contract.close_sla()
    
    details = json.loads(contract.get_details())
    assert details["status"] == "Closed"

def test_close_sla_before_expiry_fails(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(
        CONTRACT_PATH,
        direct_alice,
        direct_bob,
        "https://api.status.com",
        1000,
        500,
        "contains",
        "healthy",
        2,
        "2026-07-08T12:00:00Z"
    )
    
    # Setup funding and activate
    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    contract.deposit_collateral()
    
    direct_vm.sender = direct_bob
    direct_vm.value = 500
    contract.deposit_premium()
    
    # Warp time pre expiry
    direct_vm.warp("2026-07-08T06:00:00Z")
    import genlayer
    genlayer.gl.message_raw['datetime'] = "2026-07-08T06:00:00Z"
    
    # Attempt close should revert
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("SLA duration has not ended yet"):
        contract.close_sla()
