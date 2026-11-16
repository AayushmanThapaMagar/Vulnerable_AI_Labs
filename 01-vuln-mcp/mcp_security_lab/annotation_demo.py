import asyncio
import sys

from mcp import Client, StdioServerParameters
from mcp.types import TextContent

from mcp_security_lab.annotation_server import MARKER


async def main():
    # Reset only this exercise's synthetic marker.
    if MARKER.exists():
        MARKER.unlink()

    async with Client(
        StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_security_lab.annotation_server"],
        )
    ) as client:
        discovered = await client.list_tools()
        tool = next(
            tool
            for tool in discovered.tools
            if tool.name == "read_service_status"
        )

        print("ANNOTATIONS:", tool.annotations)
        print("MARKER BEFORE:", MARKER.exists())

        # Intentionally vulnerable policy: trust the server's claim.
        auto_approved = (
            tool.annotations is not None
            and tool.annotations.read_only_hint is True
        )

        print("AUTO-APPROVED:", auto_approved)

        if not auto_approved:
            print("STOPPED: tool requires review.")
            return

        result = await client.call_tool(tool.name, {})
        print("TOOL ERROR:", result.is_error)

        for block in result.content:
            if isinstance(block, TextContent):
                print(block.text)

        print("MARKER AFTER:", MARKER.exists())

        assert not result.is_error
        assert MARKER.read_text(encoding="utf-8") == (
            "ANNOTATION-CANARY-001\n"
        )

        print("VERIFIED: auto-approved 'read-only' tool wrote a file.")


if __name__ == "__main__":
    asyncio.run(main())