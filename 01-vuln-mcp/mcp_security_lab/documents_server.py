"""Minimal Documents MCP server."""

from mcp.server import MCPServer
from pathlib import Path

server = MCPServer("Lab Documents")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WELCOME_DOCUMENT = PROJECT_ROOT / "fixtures" / "documents" / "welcome.txt"


@server.tool()
def read_welcome_document() -> str:
    """Read the fictional company's public welcome document."""
    return WELCOME_DOCUMENT.read_text(encoding = "utf-8")


if __name__ == "__main__":
    server.run(transport="stdio")