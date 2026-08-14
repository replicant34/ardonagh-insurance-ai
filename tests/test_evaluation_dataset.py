from app.evaluation.dataset import (
    EVALUATION_CASES,
)


def test_evaluation_dataset():

    print(
        f"\nEvaluation cases: "
        f"{len(EVALUATION_CASES)}"
    )

    for case in EVALUATION_CASES:

        print(
            f"{case['id']} "
            f"→ {case['category']}"
        )

        assert "id" in case
        assert "category" in case
        assert "question" in case

    assert len(EVALUATION_CASES) >= 6