import asyncio
import json
import sys

from mcp import Client, StdioServerParameters

from mcp_security_lab.launch_trust_server import EVIDENCE


async def main():
    if EVIDENCE.exists():
        EVIDENCE.unlink()

    print("EVIDENCE BEFORE LAUNCH:", EVIDENCE.exists())

    # Synthetic secret deliberately passed to the child process.
    config = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_security_lab.launch_trust_server"],
        env={"LAB_DEMO_SECRET": "LAUNCH-CANARY-001"},
    )

    async with Client(config) as client:
        discovered = await client.list_tools()
        print("DISCOVERED:", [tool.name for tool in discovered.tools])
        print("No tools were executed.")

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    print("STARTUP EVIDENCE:", json.dumps(evidence, indent=2))

    assert evidence["synthetic_secret"] == "LAUNCH-CANARY-001"
    assert evidence["tool_called"] is False

    print("VERIFIED: startup code read the supplied synthetic secret.")
    print("Tool-call approval cannot prevent code that already ran at launch.")


if __name__ == "__main__":
    asyncio.run(main())