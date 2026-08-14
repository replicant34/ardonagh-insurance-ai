from mcp.server import MCPServer


from app.tools.insurance_tools import (
    get_active_policy_count,
    get_claim_by_id,
    analyze_claim_risk,
    search_internal_knowledge,
)


# ------------------------------------------------------------------
# MCP Server
# ------------------------------------------------------------------

mcp = MCPServer(
    "Ardonagh Insurance AI"
)


# ------------------------------------------------------------------
# MCP Tools
# ------------------------------------------------------------------

@mcp.tool()
def active_policy_count() -> int:
    """
    Return the current number of active insurance policies
    from the company insurance database.
    """

    return get_active_policy_count()

@mcp.tool()
def claim_details(claim_id: int) -> dict:
    """
    Retrieve factual details for a specific insurance claim.

    Args:
        claim_id: Internal numeric claim identifier.
    """

    return get_claim_by_id(
        claim_id=claim_id
    )


@mcp.tool()
def claim_risk_analysis(claim_id: int) -> dict:
    """
    Analyse a claim using deterministic risk indicators.

    Risk indicators are decision-support signals only
    and are not proof of fraud.

    Args:
        claim_id: Internal numeric claim identifier.
    """

    return analyze_claim_risk(
        claim_id=claim_id
    )


@mcp.tool()
def search_claims_procedure(
    query: str,
    top_k: int = 3,
) -> dict:
    """
    Search approved internal claims procedures using
    semantic retrieval.

    Args:
        query: Question or search query about internal procedures.
        top_k: Maximum number of relevant sections to retrieve.
    """

    return search_internal_knowledge(
        query=query,
        top_k=top_k,
    )


# ------------------------------------------------------------------
# Run server
# ------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()