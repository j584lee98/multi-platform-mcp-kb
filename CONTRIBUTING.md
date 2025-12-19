# Contributing

## Development Setup

1.  **Prerequisites**:
    *   Docker and Docker Compose
    *   Python 3.11+ (for local backend dev)
    *   Node.js 20+ (for local frontend dev)

2.  **Environment Variables**:
    *   Copy `.env.example` to `.env`
    *   Fill in your OAuth credentials.

3.  **Running with Docker**:
    ```bash
    make up
    ```

## Testing

*   **Backend**:
    ```bash
    make test
    ```

## Linting

*   **Run all linters**:
    ```bash
    make lint
    ```

## Project Structure

*   `frontend/`: Next.js application
*   `backend/`: FastAPI application
*   `mcp/`: MCP Servers (Google Drive, GitHub, Slack)
