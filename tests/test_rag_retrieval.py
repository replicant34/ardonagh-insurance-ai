from app.rag.retrieval import retrieve_knowledge


def test_early_claim_retrieval():

    query = (
        "What review is required when a claim "
        "happens shortly after the policy starts?"
    )

    results = retrieve_knowledge(
        query=query,
        top_k=3,
    )

    print("\nQuery:")
    print(query)

    print("\nRetrieved knowledge:")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "=" * 70)

        print(
            f"Result {index}"
        )

        print(
            f"Document: {result['document_id']}"
        )

        print(
            f"Version: {result['version']}"
        )

        print(
            f"Section: {result['section']}"
        )

        print(
            f"Distance: {result['distance']}"
        )

        print("\nContent:")
        print(result["text"])

    assert len(results) > 0

    sections = [
        result["section"]
        for result in results
    ]

    assert any(
        "Early Claims" in section
        for section in sections
    )
