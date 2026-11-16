from mcp.server import MCPServer

server = MCPServer("Lab CRM Canary")

@server.tool()
def read_customer_record() -> dict[str, str]: 
    """Read a synthetic customer record for this training lab"""
    return {
        "customer_id": "SYNTHETIC-001",
        "company": "Fictional Cedarbridge Customer",
        "classification": "confidential-training-only",
        "internal_note": "CRM-CANARY-001-NOT-For-Messaging",
    }

if __name__ == "__main__":
    server.run(transport="stdio")
