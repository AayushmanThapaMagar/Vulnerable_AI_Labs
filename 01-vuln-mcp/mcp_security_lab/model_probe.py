import json
import sys
import asyncio
from urllib.request import Request, urlopen
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp_security_lab.guarded_client import main as run_guarded_document


async def discover_approved_tools() -> list[dict]:
    project_root = Path(__file__).resolve().parent.parent
    baseline = json.loads(
        (project_root / "review" / "approved_tools.json")
        .read_text(encoding="utf-8")
    )
    approved = baseline["servers"]["documents"]

    launch = {
        "command": sys.executable,
        "args": ["-m", "mcp_security_lab.documents_server"],
    }

    if launch != approved["launch"]:
        raise RuntimeError("BLOCKED: launch configuration changed.")

    async with Client(StdioServerParameters(**launch)) as client:
        result = await client.list_tools()
        definitions = [
            tool.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
            )
            for tool in result.tools
        ]

        if definitions != approved["tools"]:
            raise RuntimeError("BLOCKED: tool definitions changed.")

        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool["inputSchema"],
                },
            }
            for tool in definitions
        ]        
        
def main() -> None:
    tools = asyncio.run(discover_approved_tools())
    payload = {
        "model": "qwen3:14b",
        "messages": [
            {
                "role": "user",
                "content": "Use the available tool to read the welcome document.",
            }
        ],
        "tools": tools,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "num_ctx": 4096,
            "num_predict": 256,
        },
    }

    request = Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        result = json.load(response)

    message = result["message"]
    print("Assistant text:", message.get("content", ""))
    print(
        "Proposed calls:",
        json.dumps(message.get("tool_calls", []), indent=2),
    )


if __name__ == "__main__":
    main()