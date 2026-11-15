import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


async def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    baseline = json.loads(
        (project_root / "review" / "approved_tools.json")
        .read_text(encoding="utf-8")
    )

    if baseline["format_version"] != 1:
        print("BLOCKED: unsupported baseline format.")
        return 1

    approved = baseline["servers"]["documents"]
    launch = {
        "command": sys.executable,
        "args": ["-m", "mcp_security_lab.documents_server"],
    }

    if launch != approved["launch"]:
        print("BLOCKED: launch configuration changed.")
        return 1

    parameters = StdioServerParameters(**launch)

    async with Client(parameters) as client:
        result = await client.list_tools()
        live_tools = [
            tool.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
            )
            for tool in result.tools
        ]

        if live_tools != approved["tools"]:
            print("BLOCKED: live tool definitions differ from approval.")
            return 1

        print("APPROVED: requesting welcome document.")
        response = await client.call_tool("read_welcome_document", {})

        for block in response.content:
            if isinstance(block, TextContent):
                print(block.text)

        return 1 if response.is_error else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))