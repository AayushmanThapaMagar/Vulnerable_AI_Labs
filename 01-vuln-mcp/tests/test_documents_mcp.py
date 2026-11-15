"""Integration checks for the Documents MCP server."""

import asyncio
import sys

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


async def check_welcome_document() -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_security_lab.documents_server"],
    )

    async with Client(parameters) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools.tools}

        assert "read_welcome_document" in tool_names

        result = await client.call_tool("read_welcome_document", {})

        assert not result.is_error, f"Tool failed: {result.content!r}"

        text = "\n".join(
            block.text
            for block in result.content
            if isinstance(block, TextContent)
        )

        expected = (
            "Welcome to Cedarbridge Labs.\n"
            "Training notice: all customer data is synthetic."
        )
        assert text.strip() == expected


def test_welcome_document_round_trip() -> None:
    asyncio.run(
        asyncio.wait_for(check_welcome_document(), timeout=30)
    )