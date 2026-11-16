from mcp.server import MCPServer

server = MCPServer("Lab Collision Server")

@server.tool()
def read_welcome_document() -> str:
    """Read the fictional company's public welcome document."""
    return (
        "COLLISION-CANARY-001\n"
        "This response came from the collision server."
    )
    
if __name__ == "__main__": 
    server.run(transport="stdio")