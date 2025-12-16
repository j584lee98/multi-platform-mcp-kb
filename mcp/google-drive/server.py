from mcp.server.fastmcp import FastMCP
import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

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

@mcp.tool()
def create_folder(token: str, name: str, parent_id: str = None) -> str:
    """
    Create a new folder in Google Drive.
    
    Args:
        token: The OAuth2 access token for the user.
        name: The name of the new folder.
        parent_id: The ID of the parent folder (optional).
    """
    try:
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        file = service.files().create(body=file_metadata, fields='id').execute()
        return f"Folder created with ID: {file.get('id')}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"

@mcp.tool()
def search_files(token: str, query: str) -> str:
    """
    Search for files in Google Drive using a query string.
    
    Args:
        token: The OAuth2 access token for the user.
        query: The search query (e.g., "name contains 'report'").
    """
    try:
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(
            q=query, pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            return "No files found matching the query."
        
        output = "Found files:\n"
        for item in items:
            output += f"{item['name']} ({item['id']}) - {item['mimeType']}\n"
        return output
    except Exception as e:
        return f"Error searching files: {str(e)}"

@mcp.tool()
def create_text_file(token: str, name: str, content: str, parent_id: str = None) -> str:
    """
    Create a new text file in Google Drive.
    
    Args:
        token: The OAuth2 access token for the user.
        name: The name of the file.
        content: The text content of the file.
        parent_id: The ID of the parent folder (optional).
    """
    try:
        creds = Credentials(token=token)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': name}
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f"File created with ID: {file.get('id')}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
