from app.tools.insurance_tools import (
    search_internal_knowledge,
)


def test_search_internal_knowledge():

    result = search_internal_knowledge(
        query=(
            "What requirements apply when "
            "an early claim is rejected?"
        )
    )

    print("\nKnowledge Tool Result:")

    print(
        f"Found: {result['found']}"
    )

    for item in result["results"]:

        print("\n" + "=" * 70)

        print(
            f"Document: {item['document_id']}"
        )

        print(
            f"Section: {item['section']}"
        )

        print(
            f"Version: {item['version']}"
        )

        print("\nContent:")
        print(item["text"])

    assert result["found"] is True

    sections = [
        item["section"]
        for item in result["results"]
    ]

    assert any(
        "Early Claims" in section
        or "Rejected Claims" in section
        for section in sections
    )