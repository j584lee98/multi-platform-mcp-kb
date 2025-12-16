# Multi-Platform MCP Knowledge Base

A full-stack application integrating Model Context Protocol (MCP) servers with a knowledge base interface. Currently features a Google Drive connector.

## Tech Stack

- **Frontend**: Next.js 15, Tailwind CSS v4, React 19
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL
- **MCP**: Python `mcp` SDK (FastMCP), Server-Sent Events (SSE) transport
- **Infrastructure**: Docker Compose

## Architecture

- `frontend`: Next.js app with authenticated sidebar layout.
- `backend`: FastAPI service handling Auth (Google OAuth) and MCP Client connections.
- `mcp/google-drive`: Standalone MCP server providing Google Drive tools (`list_files`).
- `db`: PostgreSQL database for user and token storage.

## Setup

1. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   MCP_GOOGLE_DRIVE_URL=http://mcp-google-drive:8080/sse
   ```

2. **Run with Docker**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## Features

- **Authentication**: Google OAuth login.
- **Connectors**: Dedicated page to manage Google Drive connection.
- **MCP Integration**: Connects to Google Drive MCP server to list files.
- **UI**: Responsive sidebar layout for authenticated users.
