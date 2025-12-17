from mcp.server.fastmcp import FastMCP
import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Initialize FastMCP server
mcp = FastMCP("google-drive", host="0.0.0.0", port=8080)

import json

# ... imports ...

@mcp.tool()
def list_files(token: str, folder_id: str = 'root', order_by: str = 'folder,name') -> str:
    """
    List ALL files from a Google Drive folder. Returns a JSON string.
    
    Args:
        token: The OAuth2 access token for the user.
        folder_id: The ID of the folder to list files from (default: 'root').
        order_by: Sort order (e.g., 'folder,name', 'modifiedTime desc').
    """
    try:
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        all_files = []
        page_token = None
        
        while True:
            q = f"'{folder_id}' in parents and trashed = false"
            results = service.files().list(
                q=q, 
                pageSize=1000, 
                pageToken=page_token,
                orderBy=order_by,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            all_files.extend(files)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        return json.dumps(all_files)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def search_files(token: str, query: str, order_by: str = 'folder,name') -> str:
    """
    Search for ALL matching files in Google Drive. Returns a JSON string.
    
    Args:
        token: The OAuth2 access token for the user.
        query: The search query (e.g., "name contains 'report'").
        order_by: Sort order.
    """
    try:
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        all_files = []
        page_token = None

        while True:
            results = service.files().list(
                q=query, 
                pageSize=1000, 
                pageToken=page_token,
                orderBy=order_by,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            all_files.extend(files)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        return json.dumps(all_files)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def read_file_content(token: str, file_id: str) -> str:
    """
    Read the content of a text file from Google Drive.
    
    Args:
        token: The OAuth2 access token for the user.
        file_id: The ID of the file to read.
    """
    try:
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        return file.getvalue().decode('utf-8')
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
