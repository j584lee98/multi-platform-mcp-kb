import os
from typing import Any, Dict, Optional

from auth.oauth import refresh_google_token
from langchain.agents import create_agent
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from models import OAuthToken
from pydantic import BaseModel, Field, create_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


_CHECKPOINTER = MemorySaver()


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


def _schema_has_token(schema: Any) -> bool:
    """Check if a schema (dict or Pydantic model) has a 'token' field."""
    if schema is None:
        return False
    if isinstance(schema, dict):
        # JSON schema format: check properties
        props = schema.get("properties", {})
        return "token" in props
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return "token" in schema.model_fields
    return False


def _create_pydantic_model_from_json_schema(
    schema: dict, name: str, exclude_fields: set = None
) -> type[BaseModel]:
    """Convert a JSON schema dict into a Pydantic model, optionally excluding fields."""
    if exclude_fields is None:
        exclude_fields = set()

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    field_definitions = {}
    for field_name, field_info in properties.items():
        if field_name in exclude_fields:
            continue

        # Map JSON schema types to Python types
        json_type = field_info.get("type", "string")
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        python_type = type_mapping.get(json_type, str)

        default = field_info.get("default", ...)
        if field_name not in required and default is ...:
            default = None
            python_type = Optional[python_type]

        field_definitions[field_name] = (
            python_type,
            Field(default=default, description=field_info.get("description", "")),
        )

    return create_model(name, **field_definitions)


def _provider_from_tool_name(tool_name: str) -> Optional[str]:
    """With tool_name_prefix=True, tools are named like: 'google_drive_list_files'."""
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


import re


def _clean_description(description: str) -> str:
    """Remove references to 'token' argument from tool description."""
    if not description:
        return description
    # Remove lines that mention 'token:' as a parameter
    lines = description.split("\n")
    cleaned_lines = [
        line for line in lines
        if not re.match(r"^\s*token:", line, re.IGNORECASE)
    ]
    return "\n".join(cleaned_lines)


def _wrap_tool_with_db_token(
    tool: BaseTool,
    *,
    provider: str,
    tokens_by_provider: Dict[str, str],
) -> BaseTool:
    """Wrap a tool to auto-inject the user's OAuth token, hiding it from the LLM."""
    schema = getattr(tool, "args_schema", None)

    # Only wrap tools that have a `token` arg
    if not _schema_has_token(schema):
        return tool

    # Build a new schema without the 'token' field
    if isinstance(schema, dict):
        new_schema = _create_pydantic_model_from_json_schema(
            schema, f"{tool.name}Args", exclude_fields={"token"}
        )
    else:
        # Pydantic model - remove token field
        field_definitions = {
            name: (field_info.annotation, field_info)
            for name, field_info in schema.model_fields.items()
            if name != "token"
        }
        new_schema = create_model(f"{schema.__name__}NoToken", **field_definitions)

    # Clean the description to remove token references
    cleaned_description = _clean_description(tool.description or "")

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
        description=cleaned_description,
        args_schema=new_schema,
        coroutine=call_with_token,
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

    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    llm = ChatOpenAI(model=model_name, temperature=0)

    prompt = (
        "You are a helpful assistant that can access Google Drive, GitHub, and Slack. "
        "Use the available tools to answer the user's request. "
        "Only ask for clarifying information if necessary, make assumptions otherwise. "
        "Never ask the user for OAuth tokens; authentication is handled server-side."
    )

    agent = create_agent(
        llm,
        all_tools,
        system_prompt=prompt,
        checkpointer=_CHECKPOINTER,
    )
    return agent
