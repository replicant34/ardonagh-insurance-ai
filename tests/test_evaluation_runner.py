from app.evaluation.runner import (
    run_evaluation_suite,
)


def test_evaluation_runner():

    results = run_evaluation_suite()

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    successful = sum(
        1
        for result in results
        if result["success"]
    )

    failed = len(results) - successful

    print(f"Total cases: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    for result in results:
        print(
            f"{result['id']}: "
            f"{result['duration_ms']} ms"
        )

    assert len(results) == 6