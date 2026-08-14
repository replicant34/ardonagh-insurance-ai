from app.evaluation.report import (
    generate_evaluation_report,
)


def test_evaluation_report():

    report = generate_evaluation_report()

    summary = report["summary"]
    results = report["results"]

    print("\n" + "=" * 70)
    print("AI EVALUATION REPORT")
    print("=" * 70)

    print(
        f"Total cases: "
        f"{summary['total_cases']}"
    )

    print(
        f"Execution success rate: "
        f"{summary['execution_success_rate']:.1%}"
    )

    print(
        f"Quality pass rate: "
        f"{summary['quality_pass_rate']:.1%}"
    )

    print(
        f"Average fact score: "
        f"{summary['average_fact_score']:.1%}"
    )

    print(
        f"Hallucination check pass rate: "
        f"{summary['hallucination_check_pass_rate']:.1%}"
    )

    print(
        f"Average latency: "
        f"{summary['average_latency_ms']:.2f} ms"
    )

    print(
        f"Tool selection accuracy: "
        f"{summary['tool_selection_accuracy']:.1%}"
    )

    print("\nCASE RESULTS")

    for result in results:

        print("\n" + "-" * 70)

        print(
            f"{result['id']} "
            f"[{result['category']}]"
        )

        print(
            f"Execution: "
            f"{result['execution_success']}"
        )

        print(
            f"Fact score: "
            f"{result['fact_score']:.1%}"
        )

        print(
            f"Hallucination check: "
            f"{result['hallucination_check_passed']}"
        )

        print(
            f"Quality passed: "
            f"{result['quality_passed']}"
        )

        print(
            f"Latency: "
            f"{result['duration_ms']} ms"
        )

        print(
            f"Tools used: "
            f"{result['tools_used']}"
        )

        print(
            f"Expected tools: "
            f"{result['expected_tools']}"
        )

        print(
            f"Tool selection: "
            f"{result['tool_selection_passed']}"
        )

        if result["facts_missing"]:
            print(
                "Missing facts:",
                result["facts_missing"],
            )

        if result["forbidden_claims_found"]:
            print(
                "Forbidden claims:",
                result[
                    "forbidden_claims_found"
                ],
            )

        if result["missing_tools"]:
            print(
                "Missing tools:",
                result["missing_tools"],
            )

        if result["unexpected_tools"]:
            print(
                "Unexpected tools:",
                result["unexpected_tools"],
            )

    assert summary["total_cases"] == 6