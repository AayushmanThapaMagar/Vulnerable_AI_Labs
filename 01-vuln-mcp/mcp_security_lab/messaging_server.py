import json
from pathlib import Path
from uuid import uuid4

from mcp.server import MCPServer

server = MCPServer("Lab Messaging")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTBOX = PROJECT_ROOT / "lab_state" / "messaging" / "outbox.jsonl"


@server.tool()
def send_message(receiver: str, body: str) -> dict[str, str]:
    """Record a simulated outgoing message. No message is delivered."""
    message = {
        "message_id": uuid4().hex,
        "receiver": receiver,
        "body": body,
    }

    OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOX.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(message) + "\n")

    return {
        "status": "recorded",
        "message_id": message["message_id"],
    }


if __name__ == "__main__":
    server.run(transport="stdio")