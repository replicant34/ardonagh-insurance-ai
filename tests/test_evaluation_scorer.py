from app.evaluation.scorer import (
    score_evaluation_case,
)


def test_good_answer():

    case = {
        "id": "test_good",
        "expected_facts": [
            "29012",
            "Active",
        ],
        "forbidden_claims": [
            "fraud confirmed",
        ],
    }

    result = {
        "success": True,
        "answer": (
            "There are 29012 Active "
            "insurance policies."
        ),
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nGood answer score:")
    print(score)

    assert score["fact_score"] == 1.0
    assert (
        score["hallucination_check_passed"]
        is True
    )
    assert score["quality_passed"] is True


def test_missing_fact():

    case = {
        "id": "test_missing",
        "expected_facts": [
            "29012",
            "Active",
        ],
        "forbidden_claims": [],
    }

    result = {
        "success": True,
        "answer": (
            "There are 29012 policies."
        ),
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nMissing fact score:")
    print(score)

    assert score["fact_score"] == 0.5
    assert score["quality_passed"] is False


def test_forbidden_claim():

    case = {
        "id": "test_hallucination",
        "expected_facts": [
            "Medium",
        ],
        "forbidden_claims": [
            "fraud confirmed",
        ],
    }

    result = {
        "success": True,
        "answer": (
            "Risk is Medium. "
            "Fraud confirmed."
        ),
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nForbidden claim score:")
    print(score)

    assert score["fact_score"] == 1.0

    assert (
        score["hallucination_check_passed"]
        is False
    )

    assert score["quality_passed"] is False

def test_numeric_formatting():

    case = {
        "id": "test_numeric_formatting",
        "expected_facts": [
            "29012",
        ],
        "forbidden_claims": [],
    }

    result = {
        "success": True,
        "answer": (
            "There are currently 29,012 "
            "active insurance policies."
        ),
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nNumeric formatting score:")
    print(score)

    assert score["fact_score"] == 1.0
    assert score["quality_passed"] is True

def test_correct_tool_selection():

    case = {
        "id": "test_tools",
        "expected_facts": [
            "29012",
        ],
        "forbidden_claims": [],
        "expected_tools": [
            "get_active_policy_count",
        ],
    }

    result = {
        "success": True,
        "answer": (
            "There are 29,012 active "
            "insurance policies."
        ),
        "tools_used": [
            "get_active_policy_count",
        ],
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nCorrect tool score:")
    print(score)

    assert score["tool_score"] == 1.0
    assert score["missing_tools"] == []
    assert score["unexpected_tools"] == []
    assert score["tool_selection_passed"] is True
    assert score["quality_passed"] is True


def test_unexpected_tool_selection():

    case = {
        "id": "test_wrong_tools",
        "expected_facts": [
            "29012",
        ],
        "forbidden_claims": [],
        "expected_tools": [
            "get_active_policy_count",
        ],
    }

    result = {
        "success": True,
        "answer": (
            "There are 29,012 active "
            "insurance policies."
        ),
        "tools_used": [
            "get_active_policy_count",
            "search_internal_knowledge",
        ],
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nUnexpected tool score:")
    print(score)

    assert score["tool_score"] == 1.0

    assert score["unexpected_tools"] == [
        "search_internal_knowledge",
    ]

    assert (
        score["tool_selection_passed"]
        is False
    )

    assert score["quality_passed"] is False

def test_allowed_extra_tool():

    case = {
        "id": "test_allowed_tool",
        "expected_facts": [
            "Medium",
        ],
        "forbidden_claims": [],
        "expected_tools": [
            "analyze_claim_risk",
        ],
        "allowed_tools": [
            "get_claim_by_id",
        ],
    }

    result = {
        "success": True,
        "answer": (
            "The claim has a Medium review priority."
        ),
        "tools_used": [
            "get_claim_by_id",
            "analyze_claim_risk",
        ],
    }

    score = score_evaluation_case(
        case,
        result,
    )

    print("\nAllowed extra tool score:")
    print(score)

    assert score[
        "tool_selection_passed"
    ] is True

    assert score[
        "unexpected_tools"
    ] == []

    assert score[
        "tool_score"
    ] == 1.0

    assert score[
        "quality_passed"
    ] is True