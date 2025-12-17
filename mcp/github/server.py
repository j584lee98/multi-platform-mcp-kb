from mcp.server.fastmcp import FastMCP
from github import Github
import json
import base64

# Initialize FastMCP server
# Using port 8081 to avoid conflict with google-drive on 8080 if run locally, 
# though in docker-compose they would have their own IPs.
mcp = FastMCP("github", host="0.0.0.0", port=8080) 

@mcp.tool()
def list_repos(token: str, sort: str = "updated", direction: str = "desc") -> str:
    """
    List repositories for the authenticated user. Returns a JSON string.
    
    Args:
        token: The GitHub Personal Access Token or OAuth token.
        sort: Property to sort by (created, updated, pushed, full_name).
        direction: Sort direction (asc, desc).
    """
    try:
        g = Github(token)
        user = g.get_user()
        repos = []
        # Limiting to first 100 for performance in this example, though pagination handles more
        for repo in user.get_repos(sort=sort, direction=direction):
             repos.append({
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "private": repo.private,
                "html_url": repo.html_url,
                "description": repo.description,
                "updated_at": str(repo.updated_at)
            })
             if len(repos) >= 100:
                 break
        return json.dumps(repos)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def search_repos(token: str, query: str) -> str:
    """
    Search for repositories. Returns a JSON string.
    
    Args:
        token: The GitHub Personal Access Token or OAuth token.
        query: The search query string.
    """
    try:
        g = Github(token)
        repos = []
        results = g.search_repositories(query=query)
        for repo in results:
            repos.append({
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "private": repo.private,
                "html_url": repo.html_url,
                "description": repo.description,
                "updated_at": str(repo.updated_at)
            })
            if len(repos) >= 50: # Limit results
                break
        return json.dumps(repos)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def list_issues(token: str, repo_full_name: str, state: str = "open") -> str:
    """
    List issues for a specific repository. Returns a JSON string.
    
    Args:
        token: The GitHub Personal Access Token or OAuth token.
        repo_full_name: The full name of the repository (e.g., "owner/repo").
        state: State of the issues to return (open, closed, all).
    """
    try:
        g = Github(token)
        repo = g.get_repo(repo_full_name)
        issues = []
        for issue in repo.get_issues(state=state):
            issues.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "html_url": issue.html_url,
                "created_at": str(issue.created_at),
                "user": issue.user.login if issue.user else None
            })
            if len(issues) >= 50:
                break
        return json.dumps(issues)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_file_content(token: str, repo_full_name: str, file_path: str, ref: str = None) -> str:
    """
    Get the content of a file in a repository. Returns the decoded content as a string.
    
    Args:
        token: The GitHub Personal Access Token or OAuth token.
        repo_full_name: The full name of the repository (e.g., "owner/repo").
        file_path: The path to the file in the repository.
        ref: The name of the commit/branch/tag. Default: the repository’s default branch.
    """
    try:
        g = Github(token)
        repo = g.get_repo(repo_full_name)
        if ref:
            contents = repo.get_contents(file_path, ref=ref)
        else:
            contents = repo.get_contents(file_path)
        
        if isinstance(contents, list):
            return json.dumps({"error": "Path points to a directory, not a file."})
            
        return contents.decoded_content.decode('utf-8')
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run(transport="sse")
