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

if __name__ == "__main__":
    mcp.run(transport="sse")
