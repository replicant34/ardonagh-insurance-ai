from app.evaluation.dataset import EVALUATION_CASES
from app.evaluation.runner import run_evaluation_case


def test_runner_preserves_tools():

    case = next(
        case
        for case in EVALUATION_CASES
        if case["id"] == "policy_count_001"
    )

    result = run_evaluation_case(case)

    print("\n" + "=" * 70)
    print("RUNNER METADATA TEST")
    print("=" * 70)

    print("Answer:")
    print(result["answer"])

    print("\nTools used:")
    print(result.get("tools_used"))

    print("\nFull result:")
    print(result)

    assert result["success"] is True

    assert result["tools_used"] == [
        "get_active_policy_count"
    ]