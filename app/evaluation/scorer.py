import re

def normalize_fact(value: str) -> str:
    """
    Normalize facts for deterministic comparison.

    Removes thousands separators when comparing
    purely numeric values.
    """

    text = normalize_text(value)

    # Convert values such as 29,012 -> 29012
    text = re.sub(
        r"(?<=\d),(?=\d)",
        "",
        text,
    )

    return text

def normalize_text(value: str) -> str:
    """
    Normalize text for simple deterministic comparisons.
    """
    return " ".join(
        str(value).lower().split()
    )


def score_evaluation_case(
    case: dict,
    result: dict,
) -> dict:
    """
    Score one evaluation result against the expected
    facts and forbidden claims defined in the dataset.
    """

    if not result["success"] or not result["answer"]:
        return {
            "id": case["id"],
            "execution_success": False,
            "fact_score": 0.0,
            "facts_found": [],
            "facts_missing": case.get(
                "expected_facts",
                [],
            ),
            "forbidden_claims_found": [],
            "hallucination_check_passed": False,
            "quality_passed": False,
        }

    answer = normalize_fact(result["answer"])

    expected_facts = case.get(
        "expected_facts",
        [],
    )

    facts_found = []
    facts_missing = []

    for fact in expected_facts:
        if normalize_fact(fact) in answer:
            facts_found.append(fact)
        else:
            facts_missing.append(fact)

    if expected_facts:
        fact_score = (
            len(facts_found)
            / len(expected_facts)
        )
    else:
        fact_score = 1.0

    forbidden_claims = case.get(
        "forbidden_claims",
        [],
    )

    forbidden_claims_found = []

    for claim in forbidden_claims:
        if normalize_text(claim) in answer:
            forbidden_claims_found.append(
                claim
            )

    hallucination_check_passed = (
        len(forbidden_claims_found) == 0
    )
    expected_tools = case.get(
        "expected_tools",
        [],
    )

    allowed_tools = case.get(
        "allowed_tools",
        [],
    )

    tools_used = result.get(
        "tools_used",
        [],
    )

    expected_tool_set = set(expected_tools)
    allowed_tool_set = set(allowed_tools)
    actual_tool_set = set(tools_used)

    permitted_tool_set = (
        expected_tool_set
        | allowed_tool_set
    )

    missing_tools = sorted(
        expected_tool_set - actual_tool_set
    )

    unexpected_tools = sorted(
        actual_tool_set - permitted_tool_set
    )

    if expected_tools:
        tool_score = (
            len(
                expected_tool_set
                & actual_tool_set
            )
            / len(expected_tool_set)
        )
    else:
        tool_score = (
            1.0
            if not actual_tool_set
            else 0.0
        )

    tool_selection_passed = (
        not missing_tools
        and not unexpected_tools
    )
    quality_passed = (
        fact_score == 1.0
        and hallucination_check_passed
        and tool_selection_passed
    )

    return {
        "id": case["id"],
        "execution_success": True,
        "fact_score": round(
            fact_score,
            3,
        ),
        "facts_found": facts_found,
        "facts_missing": facts_missing,
        "forbidden_claims_found": (
            forbidden_claims_found
        ),
        "hallucination_check_passed": (
            hallucination_check_passed
        ),
        "quality_passed": quality_passed,
        "expected_tools": expected_tools,
        "tools_used": tools_used,
        "tool_score": round(tool_score, 3),
        "missing_tools": missing_tools,
        "unexpected_tools": unexpected_tools,
        "tool_selection_passed": tool_selection_passed,
    }