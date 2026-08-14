from app.ai.graph import run_graph_with_metadata


def test_graph_metadata():

    result = run_graph_with_metadata(
        "How many active insurance policies "
        "do we currently have?"
    )

    print("\nGraph metadata:")
    print(result)

    assert result["answer"]
    assert "request_id" in result

    assert (
        "get_active_policy_count"
        in result["tools_used"]
    )