from app.evaluation.dataset import EVALUATION_CASES
from app.evaluation.runner import run_evaluation_suite
from app.evaluation.scorer import score_evaluation_case


def generate_evaluation_report():
    """
    Run the complete evaluation suite, score every response,
    and calculate aggregate evaluation metrics.
    """

    results = run_evaluation_suite()

    case_lookup = {
        case["id"]: case
        for case in EVALUATION_CASES
    }

    scored_results = []

    for result in results:

        case = case_lookup[result["id"]]

        score = score_evaluation_case(
            case,
            result,
        )

        scored_results.append({
            **result,
            **score,
        })

    total_cases = len(scored_results)

    successful_cases = sum(
        result["execution_success"]
        for result in scored_results
    )

    quality_passed_cases = sum(
        result["quality_passed"]
        for result in scored_results
    )

    hallucination_passed_cases = sum(
        result["hallucination_check_passed"]
        for result in scored_results
    )

    tool_selection_passed_cases = sum(
        result["tool_selection_passed"]
        for result in scored_results
    )

    average_fact_score = (
        sum(
            result["fact_score"]
            for result in scored_results
        )
        / total_cases
    )

    average_latency_ms = (
        sum(
            result["duration_ms"]
            for result in scored_results
        )
        / total_cases
    )

    summary = {
        "total_cases": total_cases,

        "execution_success_rate": round(
            successful_cases / total_cases,
            3,
        ),

        "quality_pass_rate": round(
            quality_passed_cases / total_cases,
            3,
        ),

        "average_fact_score": round(
            average_fact_score,
            3,
        ),

        "hallucination_check_pass_rate": round(
            hallucination_passed_cases
            / total_cases,
            3,
        ),

        "tool_selection_accuracy": round(
            tool_selection_passed_cases
            / total_cases,
            3,
        ),
        
        "average_latency_ms": round(
            average_latency_ms,
            2,
        ),

    }

    return {
        "summary": summary,
        "results": scored_results,
    }