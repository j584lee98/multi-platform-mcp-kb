from mcp import ClientSession
from mcp.client.sse import sse_client
import os

# In docker-compose, the service name is the hostname
MCP_SERVER_URL = os.getenv("MCP_GOOGLE_DRIVE_URL", "http://mcp-google-drive:8080/sse")

async def list_google_drive_files(token: str):
    try:
        async with sse_client(MCP_SERVER_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Call the tool
                # The tool name is defined in the MCP server (server.py)
                result = await session.call_tool("list_files", arguments={"token": token})
                
                # Result is a CallToolResult object
                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "No output from tool."
    except Exception as e:
        print(f"Error calling MCP tool: {e}")
        return f"Error: {str(e)}"
