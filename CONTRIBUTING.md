# Contributing

## Development Setup

1.  **Prerequisites**:
    *   Docker and Docker Compose (modern `docker compose` plugin)
    *   Python 3.11+ (for local backend dev)
    *   Node.js 20+ (for local frontend dev)

2.  **Environment Variables**:
    *   Copy `.env.example` to `.env`
    *   Fill in your OAuth credentials and OpenAI API key.

3.  **Running with Docker**:
    ```bash
    make up
    ```

## Makefile Commands

The `Makefile` in the root directory provides several utility commands:

- `make build`: Build all Docker images.
- `make up`: Start all services in the background.
- `make down`: Stop and remove all containers.
- `make logs`: Follow logs from all services.
- `make lint`: Run Python (Ruff) and Frontend (ESLint) linters.
- `make format`: Automatically format code and fix linting issues.
- `make test`: Run backend tests using `pytest` inside a Docker container.
- `make clean`: Remove temporary files, caches, and `node_modules`.

## Project Structure

- `frontend/`: Next.js 15 application using Tailwind CSS v4.
- `backend/`: FastAPI application.
  - `auth/`: OAuth flow and user management.
  - `chat/`: Chat API endpoints.
  - `mcp_agent.py`: LangGraph-based agent that orchestrates MCP tools.
- `mcp/`: Standalone MCP Servers.
  - Each server should have its own `Dockerfile` and `requirements.txt`.

## Adding a New MCP Connector

1.  **Create Server**: Add a new directory in `mcp/` with a `server.py` using `FastMCP`.
2.  **Dockerize**: Add a `Dockerfile` and `requirements.txt` to the new directory.
3.  **Compose**: Add the new service to `docker-compose.yml`.
4.  **Backend Integration**:
    - Update `backend/mcp_agent.py` to include the new server's URL in `SERVER_URLS`.
    - If the server requires OAuth, update `backend/auth/` to handle the new provider.
5.  **Frontend Integration**:
    - Add a new connector page in `frontend/app/(dashboard)/connectors/`.
    - Update `frontend/app/components/ConnectorStatus.tsx` to show the new connection status.

## Coding Standards

- **Python**: We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. Configuration is in `pyproject.toml`.
- **TypeScript/React**: We use ESLint and Prettier. Configuration is in `frontend/eslint.config.mjs`.

## Pull Request Process

1.  Create a new branch for your feature or bugfix.
2.  Ensure all tests pass and linting is clean (`make lint`).
3.  Update documentation if you've added new features or changed existing ones.
4.  Submit a PR with a clear description of your changes.
