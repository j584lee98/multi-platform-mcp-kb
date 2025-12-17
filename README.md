# Multi-Platform MCP Knowledge Base

A full-stack application integrating Model Context Protocol (MCP) servers with a knowledge base interface. Currently features Google Drive and GitHub connectors.

## Tech Stack

- **Frontend**: Next.js 15, Tailwind CSS v4, React 19
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL
- **MCP**: Python `mcp` SDK (FastMCP), Server-Sent Events (SSE) transport
- **Infrastructure**: Docker Compose

## Architecture

- `frontend`: Next.js app with authenticated sidebar layout.
- `backend`: FastAPI service handling Auth (Google & GitHub OAuth) and MCP Client connections.
- `mcp/google-drive`: Standalone MCP server providing Google Drive tools (`list_files`, `search_files`, `read_file_content`).
- `mcp/github`: Standalone MCP server providing GitHub tools (`list_repos`, `search_repos`, `list_issues`, `get_file_content`).
- `db`: PostgreSQL database for user and token storage.

## Setup

1. **Environment Variables**:
   Create a `.env` file in the root directory (see `.env.example`):
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@db/mcpkb
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   ```

   *Note: Configure OAuth callbacks to `http://localhost:8000/auth/google/callback` and `http://localhost:8000/auth/github/callback` respectively.*

2. **Run with Docker**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## Features

- **Authentication**: 
  - Google OAuth login
  - GitHub OAuth login
- **Connectors**: 
  - **Google Drive**: List and search files, view file metadata. Includes automatic token refresh.
  - **GitHub**: List and search repositories, view open issues.
- **MCP Integration**: 
  - Connects to Google Drive MCP server via SSE.
  - Connects to GitHub MCP server via SSE.
- **UI**: Responsive sidebar layout for authenticated users with dedicated connector pages.
