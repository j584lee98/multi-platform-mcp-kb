# Multi-Platform MCP Knowledge Base

A full-stack application integrating Model Context Protocol (MCP) servers with a knowledge base interface. This project demonstrates how to build an AI-ready knowledge base that connects to Google Drive, GitHub, and Slack using the Model Context Protocol.

## Tech Stack

- **Frontend**: Next.js 15, Tailwind CSS v4, React 19
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL
- **MCP**: Python `mcp` SDK (FastMCP), Server-Sent Events (SSE) transport
- **Infrastructure**: Docker Compose

## Architecture

- `frontend`: Next.js app with authenticated sidebar layout.
- `backend`: FastAPI service handling Auth (Google, GitHub, Slack OAuth) and MCP Client connections.
- `mcp/google-drive`: Standalone MCP server providing Google Drive tools.
- `mcp/github`: Standalone MCP server providing GitHub tools.
- `mcp/slack`: Standalone MCP server providing Slack tools.
- `db`: PostgreSQL database for user and token storage.

## Features

### Connectors & Tools

#### 1. Google Drive
- **List & Search**: Find files and folders with metadata (size, modified time, web links).
- **Content Reading**: Extract text from various file formats:
  - Google Docs (`.gdoc`)
  - PDF (`.pdf`)
  - Word (`.docx`)
  - PowerPoint (`.pptx`)
  - Excel (`.xlsx`)
  - Text files (`.txt`, `.json`, `.csv`, `.md`, etc.)
- **Direct Access**: Open files directly in Google Drive.

#### 2. GitHub
- **Repositories**: List and search repositories.
- **Issues**: List open/closed issues.
- **Pull Requests**: List PRs with status and branch details.
- **Branches**: List repository branches.
- **File Content**: Read code/text files from repositories.

#### 3. Slack
- **Channels**: List public/private channels and DMs.
- **Users**: List workspace users to map IDs to names.
- **History**: Fetch message history from channels.
- **Threads**: Retrieve full thread replies for deep context.
- **Search**: Search messages across the workspace.

## Setup

1. **Environment Variables**:
   Create a `.env` file in the root directory (see `.env.example`):
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@db/mcpkb
   
   # Google OAuth
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   
   # GitHub OAuth
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   
   # Slack OAuth
   SLACK_CLIENT_ID=your_slack_client_id
   SLACK_CLIENT_SECRET=your_slack_client_secret
   ```

   *Note: Configure OAuth callbacks:*
   - Google: `http://localhost:8000/auth/google/callback`
   - GitHub: `http://localhost:8000/auth/github/callback`
   - Slack: `http://localhost:8000/auth/slack/callback`

2. **Slack Scopes**:
   Ensure your Slack App has the following User Token Scopes:
   - `channels:history`, `channels:read`
   - `groups:history`, `groups:read`
   - `im:history`, `im:read`
   - `mpim:history`, `mpim:read`
   - `users:read`
   - `search:read`

3. **Run with Docker**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## MCP Integration

The project uses the Model Context Protocol to standardize how the backend communicates with external services. Each service (Google Drive, GitHub, Slack) runs as an independent MCP server container. The backend acts as an MCP Client, connecting to these servers via SSE (Server-Sent Events) to execute tools.

This architecture allows for:
- **Modularity**: Each connector is isolated.
- **Scalability**: Connectors can be deployed independently.
- **AI Readiness**: The tools are defined in a standard format that LLMs can easily understand and invoke.
