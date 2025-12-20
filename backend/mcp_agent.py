import os
from typing import Any, Dict, Optional

from auth.oauth import refresh_google_token
from langchain.agents import create_agent
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from models import OAuthToken
from pydantic import BaseModel, create_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


# Define URLs
MCP_GOOGLE_DRIVE_URL = os.getenv(
    "MCP_GOOGLE_DRIVE_URL",
    "http://mcp-google-drive:8080/sse",
)
MCP_GITHUB_URL = os.getenv("MCP_GITHUB_URL", "http://mcp-github:8080/sse")
MCP_SLACK_URL = os.getenv("MCP_SLACK_URL", "http://mcp-slack:8080/sse")

SERVER_URLS = {
    "google_drive": MCP_GOOGLE_DRIVE_URL,
    "github": MCP_GITHUB_URL,
    "slack": MCP_SLACK_URL,
}

PROVIDER_BY_SERVER: Dict[str, str] = {
    "google_drive": "google",
    "github": "github",
    "slack": "slack",
}


def _args_schema_without_token(
    schema: type[BaseModel] | None,
) -> type[BaseModel] | None:
    if schema is None:
        return None
    if not issubclass(schema, BaseModel):
        return schema
    if "token" not in schema.model_fields:
        return schema

    field_definitions = {
        name: (field_info.annotation, field_info)
        for name, field_info in schema.model_fields.items()
        if name != "token"
    }
    return create_model(f"{schema.__name__}NoToken", **field_definitions)


def _provider_from_tool_name(tool_name: str) -> Optional[str]:
    # With tool_name_prefix=True, tools are named like: "google_drive_list_files".
    for server, provider in PROVIDER_BY_SERVER.items():
        if tool_name.startswith(f"{server}_"):
            return provider
    return None


async def _load_user_access_tokens(db: AsyncSession, user_id: int) -> Dict[str, str]:
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user_id))
    records = list(result.scalars().all())
    by_provider = {r.provider: r for r in records}

    tokens: Dict[str, str] = {}
    for provider in ("google", "github", "slack"):
        record = by_provider.get(provider)
        if not record:
            continue
        if provider == "google":
            tokens[provider] = await refresh_google_token(record, db)
        else:
            tokens[provider] = record.access_token
    return tokens


def _wrap_tool_with_db_token(
    tool: BaseTool,
    *,
    provider: str,
    tokens_by_provider: Dict[str, str],
) -> BaseTool:
    # Only wrap tools that have a `token` arg.
    if not getattr(tool, "args_schema", None) or not issubclass(tool.args_schema, BaseModel):
        return tool
    if "token" not in tool.args_schema.model_fields:
        return tool

    new_schema = _args_schema_without_token(tool.args_schema)

    async def call_with_token(**arguments: Any):
        access_token = tokens_by_provider.get(provider)
        if not access_token:
            raise ToolException(
                f"{provider} is not connected for this user. Connect it in the Connectors page first."
            )
        merged = dict(arguments)
        merged["token"] = access_token
        return await tool.ainvoke(merged)

    return StructuredTool(
        name=tool.name,
        description=tool.description or "",
        args_schema=new_schema,
        coroutine=call_with_token,
        response_format=getattr(tool, "response_format", None),
        metadata=getattr(tool, "metadata", None),
    )


async def create_mcp_agent(*, user_id: int, db: AsyncSession):
    # Load tokens once per request so tool calls don't leak tokens to the LLM
    # and to avoid AsyncSession concurrency issues if tools run in parallel.
    tokens_by_provider = await _load_user_access_tokens(db, user_id)

    all_tools: list[BaseTool] = []
    for server_name, url in SERVER_URLS.items():
        try:
            tools = await load_mcp_tools(
                session=None,
                connection={"transport": "sse", "url": url},
                server_name=server_name,
                tool_name_prefix=True,
            )

            for tool in tools:
                provider = _provider_from_tool_name(tool.name)
                if provider is None:
                    all_tools.append(tool)
                else:
                    all_tools.append(
                        _wrap_tool_with_db_token(
                            tool,
                            provider=provider,
                            tokens_by_provider=tokens_by_provider,
                        )
                    )
        except Exception as e:
            print(f"Failed to load tools from {server_name}: {e}")

    if not all_tools:
        print("Warning: No tools found from any MCP server.")

    model_name = os.getenv("OPENAI_MODEL")
    llm = ChatOpenAI(model=model_name, temperature=0)

    prompt = (
        "You are a helpful assistant that can access Google Drive, GitHub, and Slack. "
        "Use the available tools to answer the user's request. "
        "Only ask for clarifying information if necessary, make assumptions otherwise. "
        "Never ask the user for OAuth tokens; authentication is handled server-side."
    )

    agent = create_agent(llm, all_tools, system_prompt=prompt)
    return agent
