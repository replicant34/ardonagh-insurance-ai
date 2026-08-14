import time

from app.ai.graph import run_graph_with_metadata
from app.evaluation.dataset import EVALUATION_CASES


def run_evaluation_case(case: dict) -> dict:
    """
    Run one evaluation case through the LangGraph agent
    and capture its answer, tool usage, execution status,
    and latency.
    """

    start_time = time.perf_counter()

    try:
        graph_result = run_graph_with_metadata(
            case["question"]
        )

        answer = graph_result["answer"]
        tools_used = graph_result.get(
            "tools_used",
            [],
        )

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "answer": answer,
            "tools_used": tools_used,
            "duration_ms": round(duration_ms, 2),
            "success": True,
            "error": None,
        }

    except Exception as exc:

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "answer": None,
            "tools_used": [],
            "duration_ms": round(duration_ms, 2),
            "success": False,
            "error": str(exc),
        }


def run_evaluation_suite() -> list[dict]:
    """
    Run the complete evaluation dataset.
    """

    results = []

    for case in EVALUATION_CASES:

        print("\n" + "=" * 70)
        print(f"Running: {case['id']}")
        print(f"Category: {case['category']}")
        print(f"Question: {case['question']}")

        result = run_evaluation_case(case)

        results.append(result)

        print(f"Success: {result['success']}")
        print(
            f"Duration: "
            f"{result['duration_ms']} ms"
        )

        print(
            f"Tools used: "
            f"{result['tools_used']}"
        )

        if result["success"]:
            print("\nAnswer:")
            print(result["answer"])
        else:
            print("\nError:")
            print(result["error"])

    return results