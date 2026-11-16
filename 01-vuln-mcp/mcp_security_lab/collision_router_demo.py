import asyncio
import sys
from contextlib import AsyncExitStack

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


SERVERS = {
    "documents": "mcp_security_lab.documents_server",
    "collision": "mcp_security_lab.collision_server",
}


async def main():
    async with AsyncExitStack() as stack:
        routes = {}

        for server_name, module in SERVERS.items():
            client = await stack.enter_async_context(
                Client(
                    StdioServerParameters(
                        command=sys.executable,
                        args=["-m", module],
                    )
                )
            )

            discovered = await client.list_tools()

            for tool in discovered.tools:
                if tool.name in routes:
                    previous_server = routes[tool.name][0]
                    print(
                        f"OVERWRITE: {tool.name}: "
                        f"{previous_server} -> {server_name}"
                    )

                # Intentionally vulnerable: server identity is omitted.
                routes[tool.name] = (server_name, client, tool.name)

        requested_tool = "read_welcome_document"
        server_name, client, actual_name = routes[requested_tool]

        print("REQUESTED TOOL:", requested_tool)
        print("ROUTED TO:", server_name)

        result = await client.call_tool(actual_name, {})
        text = "\n".join(
            block.text
            for block in result.content
            if isinstance(block, TextContent)
        )

        print("TOOL ERROR:", result.is_error)
        print("TOOL RESULT:", text)

        assert not result.is_error
        assert server_name == "collision"
        assert "COLLISION-CANARY-001" in text

        print("VERIFIED: duplicate name overwrote the documents route.")


if __name__ == "__main__":
    asyncio.run(main())