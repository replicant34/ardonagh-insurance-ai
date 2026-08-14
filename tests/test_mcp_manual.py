import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """
    Start the Insurance MCP server as a subprocess,
    discover its tools, and test the available MCP tools.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp_server.server",
        ],
        env={
            **os.environ,
            "PYTHONPATH": ".",
        },
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            # Establish MCP connection
            await session.initialize()

            print("\nMCP connection established.")

            # Discover tools exposed by the server
            tools_response = await session.list_tools()

            print("\nAvailable MCP tools:")

            for tool in tools_response.tools:
                print(f"- {tool.name}")


            # ---------------------------------------------------------
            # Test 1: Active policy count
            # ---------------------------------------------------------

            result = await session.call_tool(
                "active_policy_count",
                arguments={},
            )

            print("\n" + "=" * 70)
            print("ACTIVE POLICY COUNT")
            print(result.structured_content)


            # ---------------------------------------------------------
            # Test 2: Claim details
            # ---------------------------------------------------------

            result = await session.call_tool(
                "claim_details",
                arguments={
                    "claim_id": 16,
                },
            )

            print("\n" + "=" * 70)
            print("CLAIM DETAILS")
            print("is_error:", result.is_error)
            print("structured_content:", result.structured_content)
            print("content:", result.content)


            # ---------------------------------------------------------
            # Test 3: Claim risk analysis
            # ---------------------------------------------------------

            result = await session.call_tool(
                "claim_risk_analysis",
                arguments={
                    "claim_id": 16,
                },
            )

            print("\n" + "=" * 70)
            print("CLAIM RISK ANALYSIS")
            print("is_error:", result.is_error)
            print("structured_content:", result.structured_content)
            print("content:", result.content)


            # ---------------------------------------------------------
            # Test 4: Internal procedure / RAG
            # ---------------------------------------------------------

            result = await session.call_tool(
                "search_claims_procedure",
                arguments={
                    "query": (
                        "What requirements apply when "
                        "an early claim is rejected?"
                    ),
                    "top_k": 3,
                },
            )

            print("\n" + "=" * 70)
            print("CLAIMS PROCEDURE SEARCH")
            print("is_error:", result.is_error)
            print("structured_content:", result.structured_content)
            print("content:", result.content)


if __name__ == "__main__":
    asyncio.run(main())