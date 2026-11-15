"""Call the Documents server directly, without a model."""

import asyncio
import sys

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


async def main() -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_security_lab.documents_server"],
    )

    async with Client(parameters) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools.tools])

        result = await client.call_tool("read_welcome_document", {})
        print("Tool error:", result.is_error)

        for block in result.content:
            if isinstance(block, TextContent):
                print(block.text)

        if result.is_error:
            raise RuntimeError("The welcome document tool failed.")


if __name__ == "__main__":
    asyncio.run(main())