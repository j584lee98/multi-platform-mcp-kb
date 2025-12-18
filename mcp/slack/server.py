from mcp.server.fastmcp import FastMCP
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json

# Initialize FastMCP server
mcp = FastMCP("slack", host="0.0.0.0", port=8080)

@mcp.tool()
def list_channels(token: str, types: str = "public_channel,private_channel,im,mpim") -> str:
    """
    List public and private channels, DMs, and MPIMs in the workspace.
    
    Args:
        token: The Slack User OAuth Token.
        types: Comma-separated list of channel types to include.
    """
    try:
        client = WebClient(token=token)
        response = client.conversations_list(types=types, limit=100)
        channels = []
        for channel in response["channels"]:
            # Filter for channels the user is a member of
            # Note: is_member is true for public/private channels the user is in.
            # For IMs (DMs), is_member might not be present, but the user is implicitly a member.
            if not channel.get("is_im") and not channel.get("is_member"):
                continue

            # For IMs, name might be empty, use user ID or fetch user name if possible
            name = channel.get("name")
            if not name and channel.get("is_im"):
                name = f"DM: {channel.get('user')}"
            
            channels.append({
                "id": channel["id"],
                "name": name or "Unnamed Channel",
                "is_channel": channel.get("is_channel", False),
                "is_group": channel.get("is_group", False),
                "is_im": channel.get("is_im", False),
                "num_members": channel.get("num_members", 0),
                "topic": channel.get("topic", {}).get("value", ""),
                "purpose": channel.get("purpose", {}).get("value", "")
            })
        return json.dumps(channels)
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_channel_history(token: str, channel_id: str, limit: int = 50) -> str:
    """
    Fetch message history from a channel.
    
    Args:
        token: The Slack Bot User OAuth Token (xoxb-...).
        channel_id: The ID of the channel to fetch history from.
        limit: Number of messages to fetch.
    """
    try:
        client = WebClient(token=token)
        response = client.conversations_history(channel=channel_id, limit=limit)
        messages = []
        for msg in response["messages"]:
            messages.append({
                "ts": msg.get("ts"),
                "user": msg.get("user"),
                "text": msg.get("text"),
                "type": msg.get("type"),
                "thread_ts": msg.get("thread_ts")
            })
        return json.dumps(messages)
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_thread_replies(token: str, channel_id: str, thread_ts: str) -> str:
    """
    Fetch replies from a specific message thread.
    
    Args:
        token: The Slack Bot User OAuth Token.
        channel_id: The ID of the channel containing the thread.
        thread_ts: The timestamp of the parent message.
    """
    try:
        client = WebClient(token=token)
        response = client.conversations_replies(channel=channel_id, ts=thread_ts)
        messages = []
        for msg in response["messages"]:
            messages.append({
                "ts": msg.get("ts"),
                "user": msg.get("user"),
                "text": msg.get("text"),
                "type": msg.get("type"),
                "thread_ts": msg.get("thread_ts")
            })
        return json.dumps(messages)
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def search_messages(token: str, query: str, count: int = 20) -> str:
    """
    Search for messages matching a query.
    
    Args:
        token: The Slack User OAuth Token.
        query: The search query.
        count: Number of results to return.
    """
    try:
        client = WebClient(token=token)
        response = client.search_messages(query=query, count=count)
        matches = []
        for match in response["messages"]["matches"]:
            matches.append({
                "ts": match.get("ts"),
                "user": match.get("user"),
                "username": match.get("username"),
                "text": match.get("text"),
                "channel": match.get("channel", {}).get("name"),
                "permalink": match.get("permalink")
            })
        return json.dumps(matches)
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def list_users(token: str) -> str:
    """
    List all users in the workspace to map IDs to names.
    
    Args:
        token: The Slack Bot User OAuth Token.
    """
    try:
        client = WebClient(token=token)
        response = client.users_list()
        users = []
        for user in response["members"]:
            if user.get("deleted"):
                continue
            users.append({
                "id": user["id"],
                "name": user.get("name"),
                "real_name": user.get("real_name"),
                "is_bot": user.get("is_bot")
            })
        return json.dumps(users)
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run(transport="sse")
