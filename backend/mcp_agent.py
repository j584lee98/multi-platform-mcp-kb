import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools

# Define URLs
MCP_GOOGLE_DRIVE_URL = os.getenv("MCP_GOOGLE_DRIVE_URL", "http://mcp-google-drive:8080/sse")
MCP_GITHUB_URL = os.getenv("MCP_GITHUB_URL", "http://mcp-github:8080/sse")
MCP_SLACK_URL = os.getenv("MCP_SLACK_URL", "http://mcp-slack:8080/sse")

SERVER_URLS = {
    "google_drive": MCP_GOOGLE_DRIVE_URL,
    "github": MCP_GITHUB_URL,
    "slack": MCP_SLACK_URL,
}

async def create_mcp_agent():
    all_tools = []
    for name, url in SERVER_URLS.items():
        try:
            # load_mcp_tools will connect to the server, list tools, and create LangChain tools
            # that establish a new connection for each tool call (since session is None).
            tools = await load_mcp_tools(
                session=None,
                connection={"transport": "sse", "url": url},
                server_name=name
            )
            all_tools.extend(tools)
        except Exception as e:
            print(f"Failed to load tools from {name}: {e}")
    
    if not all_tools:
        print("Warning: No tools found from any MCP server.")

    model_name = os.getenv("OPENAI_MODEL")
    llm = ChatOpenAI(model=model_name, temperature=0)
    
    prompt = """You are a helpful assistant that can access
    Google Drive, GitHub, and Slack. Use the available tools
    to answer the user's request.
    """

    agent = create_agent(llm, all_tools, system_prompt=prompt)
    
    return agent
