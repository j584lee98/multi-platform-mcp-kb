from mcp.server.fastmcp import FastMCP
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Initialize FastMCP server
mcp = FastMCP("google-drive", host="0.0.0.0", port=8080)

@mcp.tool()
def list_files(token: str, page_size: int = 10) -> str:
    """
    List files from Google Drive.
    
    Args:
        token: The OAuth2 access token for the user.
        page_size: Number of files to return.
    """
    try:
        # Create credentials object from token
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            return "No files found."
        
        output = "Files:\n"
        for item in items:
            output += f"{item['name']} ({item['id']})\n"
        return output
    except Exception as e:
        return f"Error listing files: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
