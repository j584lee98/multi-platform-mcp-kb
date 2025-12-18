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

async def search_google_drive_files(token: str, query: str):
    return await call_google_drive_tool("search_files", {"token": token, "query": query})

async def read_google_drive_file(token: str, file_id: str):
    return await call_google_drive_tool("read_file_content", {"token": token, "file_id": file_id})

# GitHub Tools
async def list_github_repos(token: str):
    return await call_github_tool("list_repos", {"token": token})

async def list_github_branches(token: str, repo_full_name: str):
    return await call_github_tool("list_branches", {"token": token, "repo_full_name": repo_full_name})

async def list_github_pull_requests(token: str, repo_full_name: str, state: str = "open"):
    return await call_github_tool("list_pull_requests", {"token": token, "repo_full_name": repo_full_name, "state": state})

async def list_github_issues(token: str, repo_full_name: str, state: str = "open"):
    return await call_github_tool("list_issues", {"token": token, "repo_full_name": repo_full_name, "state": state})

async def get_github_file_content(token: str, repo_full_name: str, file_path: str, ref: str = None):
    args = {"token": token, "repo_full_name": repo_full_name, "file_path": file_path}
    if ref:
        args["ref"] = ref
    return await call_github_tool("get_file_content", args)

# Slack Tools
async def list_slack_channels(token: str):
    return await call_slack_tool("list_channels", {"token": token})

async def list_slack_users(token: str):
    return await call_slack_tool("list_users", {"token": token})

async def get_slack_channel_history(token: str, channel_id: str):
    return await call_slack_tool("get_channel_history", {"token": token, "channel_id": channel_id})

async def get_slack_thread_replies(token: str, channel_id: str, thread_ts: str):
    return await call_slack_tool("get_thread_replies", {"token": token, "channel_id": channel_id, "thread_ts": thread_ts})

async def search_slack_messages(token: str, query: str):
    return await call_slack_tool("search_messages", {"token": token, "query": query})

