from mcp import ClientSession
from mcp.client.sse import sse_client
import os

# In docker-compose, the service name is the hostname
MCP_GOOGLE_DRIVE_URL = os.getenv("MCP_GOOGLE_DRIVE_URL", "http://mcp-google-drive:8080/sse")
MCP_GITHUB_URL = os.getenv("MCP_GITHUB_URL", "http://mcp-github:8080/sse")

async def call_google_drive_tool(tool_name: str, arguments: dict):
    try:
        async with sse_client(MCP_GOOGLE_DRIVE_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Call the tool
                result = await session.call_tool(tool_name, arguments=arguments)
                
                # Result is a CallToolResult object
                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "No output from tool."
    except Exception as e:
        print(f"Error calling MCP tool {tool_name}: {e}")
        return f"Error: {str(e)}"

async def call_github_tool(tool_name: str, arguments: dict):
    try:
        async with sse_client(MCP_GITHUB_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Call the tool
                result = await session.call_tool(tool_name, arguments=arguments)
                
                # Result is a CallToolResult object
                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "No output from tool."
    except Exception as e:
        print(f"Error calling MCP tool {tool_name}: {e}")
        return f"Error: {str(e)}"

async def list_google_drive_files(token: str, folder_id: str = 'root'):
    return await call_google_drive_tool("list_files", {"token": token, "folder_id": folder_id})

