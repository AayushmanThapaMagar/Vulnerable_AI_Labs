"""Minimal CRM MCP server using synthetic training data."""

from mcp.server import MCPServer 

server = MCPServer("Lab CRM")

CUSTOMERS = {
    "cust-001": {
        "customer_id" : "cust-001",
        "company": "Junper Bakery",
        "account_notes": "Request a demonstration of the training platform"
    }
}

@server.tool()
def get_customer(customer_id: str) -> dict[str, str]:
    """Retrieve a fictional training customer by its customer ID."""
    if customer_id not in CUSTOMERS:
        raise ValueError("Customer not found.")
    
    return CUSTOMERS[customer_id].copy()

if __name__ == "__main__":
    server.run(transport="stdio")