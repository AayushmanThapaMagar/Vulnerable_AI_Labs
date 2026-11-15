"""Record tool definations from our explicity configured lab servers."""

import asyncio 
import json
import sys

from mcp import Client, StdioServerParameters

LAB_SERVERS = {
    "documents": "mcp_security_lab.documents_server", 
    "crm": "mcp_security_lab.crm_server",
}

async def discover_tools() -> dict: 
    inventory = {
        "format_version": 1,
        "servers": {},
    }
    
    for server_id, module in LAB_SERVERS.items():
        parameters = StdioServerParameters(
            command = sys.executable,
            args = ["-m", module],
        )
        
        async with Client(parameters) as client: 
            results = await client.list_tools()
            
            definations = [
                tool.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_none=True,
                )
                for tool in results.tools
            ]
            
            inventory["servers"][server_id] = {
                "launch" : {
                    "command" : sys.executable,
                    "args": ["-m", module],
                },
                "tools": definations,
            }
        
    return inventory

async def main() -> None:
    inventory = await asyncio.wait_for(discover_tools(), timeout=30)
    print(json.dumps(inventory, indent=2, sort_keys=2))
    
if __name__ == "__main__":
    asyncio.run(main())