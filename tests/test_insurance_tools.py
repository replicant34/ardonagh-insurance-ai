from app.tools.insurance_tools import get_active_policy_count
from app.tools.insurance_tools import get_policy_by_number

from app.tools.insurance_tools import (
    get_active_policy_count,
    get_total_premium,
    get_total_claims,
    get_loss_ratio,
    get_policy_by_number,
    get_claim_by_id,
    analyze_claim_risk,
)


def test_get_active_policy_count():

    count = get_active_policy_count()

    print(f"\nActive policies: {count}")

    assert isinstance(count, int)
    assert count >= 0


def test_get_total_premium():

    premium = get_total_premium()

    print(f"\nTotal premium: {premium:,.2f}")

    assert isinstance(premium, float)
    assert premium >= 0


def test_get_total_claims():

    claims = get_total_claims()

    print(f"\nTotal claims: {claims:,.2f}")

    assert isinstance(claims, float)
    assert claims >= 0


def test_get_loss_ratio():

    loss_ratio = get_loss_ratio()

    print(f"\nLoss ratio: {loss_ratio:.2f}%")

    assert isinstance(loss_ratio, float)
    assert loss_ratio >= 0

def test_get_policy_by_number():

    policy_number = "POL-00000005"

    policy = get_policy_by_number(policy_number)

    print("\nPolicy:")
    print(policy)

    assert isinstance(policy, dict)
    assert policy["found"] is True
    assert policy["policy_number"] == policy_number

def test_get_claim_by_id():

    claim_id = 16  # Replace if ClaimID 1 does not exist

    claim = get_claim_by_id(claim_id)

    print("\nClaim:")
    print(claim)

    assert isinstance(claim, dict)
    assert claim["found"] is True
    assert claim["claim_id"] == claim_id

def test_analyze_claim_risk():

    claim_id = 16

    analysis = analyze_claim_risk(claim_id)

    print("\nClaim Risk Analysis:")
    print(analysis)

    assert isinstance(analysis, dict)
    assert analysis["found"] is True
    assert analysis["claim_id"] == claim_id

    assert analysis["review_priority"] in [
        "Low",
        "Medium",
        "High",
    ]

    assert isinstance(
        analysis["risk_indicators"],
        list,
    )