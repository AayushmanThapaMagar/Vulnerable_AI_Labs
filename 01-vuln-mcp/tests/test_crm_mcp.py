"""Integration checks for the CRM MCP server."""

import asyncio
import sys

from mcp import Client, StdioServerParameters


async def check_customer_lookup() -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_security_lab.crm_server"],
    )

    async with Client(parameters) as client:
        tools = await client.list_tools()
        assert "get_customer" in {tool.name for tool in tools.tools}

        existing = await client.call_tool(
            "get_customer",
            {"customer_id": "cust-001"},
        )

        assert not existing.is_error, existing.content
        assert existing.structured_content == {
            "customer_id": "cust-001",
            "company": "Junper Bakery",
            "account_notes": "Request a demonstration of the training platform",
        }

        missing = await client.call_tool(
            "get_customer",
            {"customer_id": "cust-missing"},
        )

        assert missing.is_error, "An unknown customer must not succeed."


def test_customer_lookup_round_trip() -> None:
    asyncio.run(
        asyncio.wait_for(check_customer_lookup(), timeout=30)
    )