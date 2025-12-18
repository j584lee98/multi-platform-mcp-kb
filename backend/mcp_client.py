from mcp import ClientSession
from mcp.client.sse import sse_client
import os

# In docker-compose, the service name is the hostname
MCP_GOOGLE_DRIVE_URL = os.getenv("MCP_GOOGLE_DRIVE_URL", "http://mcp-google-drive:8080/sse")
MCP_GITHUB_URL = os.getenv("MCP_GITHUB_URL", "http://mcp-github:8080/sse")
MCP_SLACK_URL = os.getenv("MCP_SLACK_URL", "http://mcp-slack:8080/sse")

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

async def call_slack_tool(tool_name: str, arguments: dict):
    try:
        async with sse_client(MCP_SLACK_URL) as (read_stream, write_stream):
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

async def list_slack_channels(token: str):
    return await call_slack_tool("list_channels", {"token": token})

async def get_slack_channel_history(token: str, channel_id: str):
    return await call_slack_tool("get_channel_history", {"token": token, "channel_id": channel_id})

