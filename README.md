# Docker Agent Backend

A lightweight, secure, and extensible backend agent built with **FastAPI** that lets you manage and monitor Docker containers remotely — via both **REST APIs** and **real-time WebSocket streaming**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ahmed-gelemli/docker-agent-backend)

## Features

- List Docker containers
- View container details and logs
- Start / stop / restart containers
- Real-time log streaming via WebSocket
- Stream live container stats
- Docker events stream (start/stop/etc)
- List images
- **MCP (Model Context Protocol)** support for AI assistants
- **API versioning** (`/api/v1/`)
- **JWT authentication** with token expiration
- **Rate limiting** to prevent abuse
- **CORS** configuration
- **Request tracing** with unique request IDs
- **Structured logging** (JSON in production)
- **Production-ready** Docker setup (non-root, health checks)

---

## API Overview

> **Note:** All endpoints are prefixed with `/api/v1`

### Auth

| Method | Endpoint            | Description                     | Auth Required |
|--------|---------------------|---------------------------------|---------------|
| POST   | `/api/v1/auth/login`  | Get JWT token                   | No            |
| GET    | `/api/v1/auth/check`  | Validate token & get user info  | Yes           |

### Containers

| Method | Endpoint                          | Description               | Rate Limit |
|--------|-----------------------------------|---------------------------|------------|
| GET    | `/api/v1/containers/`             | List all containers       | 60/min     |
| GET    | `/api/v1/containers/{id}`         | Get container details     | 60/min     |
| GET    | `/api/v1/containers/{id}/logs`    | View container logs       | 60/min     |
| POST   | `/api/v1/containers/{id}/start`   | Start container           | 10/min     |
| POST   | `/api/v1/containers/{id}/stop`    | Stop container            | 10/min     |
| POST   | `/api/v1/containers/{id}/restart` | Restart container         | 10/min     |

### Stats & System

| Method | Endpoint              | Description                              | Auth Required |
|--------|-----------------------|------------------------------------------|---------------|
| GET    | `/api/v1/stats/{id}`  | CPU, memory, network, I/O stats          | Yes           |
| GET    | `/api/v1/version`     | Docker version, API version, OS, arch    | Yes           |
| GET    | `/api/v1/healthz`     | Basic health check                       | No            |
| GET    | `/api/v1/health`      | Enhanced health with system info         | Yes           |

### Images

| Method | Endpoint           | Description          |
|--------|--------------------|----------------------|
| GET    | `/api/v1/images/`  | List Docker images   |

### WebSocket Endpoints

Real-time streaming with JWT token passed as query parameter.

| Path                                    | Description                 |
|-----------------------------------------|-----------------------------|
| `/api/v1/logs/ws/{id}?token=JWT`        | Stream live logs            |
| `/api/v1/stats/ws/{id}?token=JWT`       | Stream live CPU/memory      |
| `/api/v1/events/ws?token=JWT`           | Stream Docker events        |

### MCP (Model Context Protocol)

Enables AI assistants (Claude, Cursor, etc.) to interact with Docker via the MCP protocol.

| Path                  | Description                              | Auth              |
|-----------------------|------------------------------------------|-------------------|
| `GET /mcp/sse`        | SSE endpoint for MCP connection          | API Key (Bearer)  |
| `POST /mcp/messages/` | Handle MCP messages                      | API Key (Bearer)  |

**Available MCP Tools:**

| Tool                  | Description                                      |
|-----------------------|--------------------------------------------------|
| `docker_health`       | Get Docker daemon health and system info         |
| `docker_version`      | Get Docker version information                   |
| `list_containers`     | List all containers with status and ports        |
| `get_container`       | Get detailed container info                      |
| `get_container_logs`  | Get container logs                               |
| `get_container_stats` | Get container CPU/memory/network stats           |
| `list_images`         | List all Docker images                           |
| `start_container`     | Start a stopped container                        |
| `stop_container`      | Stop a running container                         |
| `restart_container`   | Restart a container                              |

---

## Installation

### Using Docker Compose (Recommended)

```bash
# Clone the repo
git clone https://github.com/ahmed-gelemli/docker-agent-backend.git
cd docker-agent-backend

# Create environment file
cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
API_USERNAME=admin
API_PASSWORD=your_secure_password
EOF

# Build and run
docker compose up --build -d
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Configuration section)

# Run development server
python run.py
```

---

## Configuration

Create a `.env` file in the project root:

```env
# REQUIRED - Generate with: openssl rand -base64 32
SECRET_KEY=your-secret-key-at-least-32-characters

# API Credentials
API_USERNAME=admin
API_PASSWORD=your_secure_password

# JWT Settings (optional)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (optional) - comma-separated origins
CORS_ORIGINS=https://your-dashboard.com,https://another-origin.com

# Rate Limiting (optional)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# MCP Configuration
MCP_ENABLED=true
MCP_API_KEY=your-mcp-api-key-at-least-16-chars  # Generate with: openssl rand -base64 32
MCP_DEBUG=false

# Application (optional)
DEBUG=false
APP_NAME=Docker Agent
```

---

## Usage

### 1. Get a JWT Token

```bash
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Use the Token

```bash
# List containers
curl http://localhost:9000/api/v1/containers/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "containers": [
    {
      "id": "9a2dd44bdbed",
      "name": "my-container",
      "image": "nginx:latest",
      "status": "running",
      "state": "running",
      "created": 1735123456,
      "ports": []
    }
  ],
  "total": 1
}
```

```bash
# Get container details
curl http://localhost:9000/api/v1/containers/CONTAINER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "id": "9a2dd44bdbedabc123...",
  "short_id": "9a2dd44bdbed",
  "name": "my-container",
  "image": "nginx:latest",
  "status": "running",
  "state": {
    "status": "running",
    "running": true,
    "paused": false,
    "pid": 12345,
    "exit_code": 0
  },
  "config": {
    "hostname": "9a2dd44bdbed",
    "env": ["PATH=/usr/local/bin", "NGINX_VERSION=1.25"],
    "cmd": ["nginx", "-g", "daemon off;"],
    "labels": {}
  },
  "mounts": [],
  "networks": {
    "bridge": {
      "ip_address": "172.17.0.2",
      "gateway": "172.17.0.1"
    }
  },
  "ports": []
}
```

```bash
# Get enhanced health check
curl http://localhost:9000/api/v1/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "status": "ok",
  "docker_connected": true,
  "docker_version": "24.0.7",
  "api_version": "1.43",
  "os": "linux",
  "arch": "amd64",
  "containers_running": 3,
  "containers_total": 5,
  "images_total": 12,
  "memory_total": 16777216000,
  "cpus": 8
}
```

```bash
# Restart a container
curl -X POST http://localhost:9000/api/v1/containers/CONTAINER_ID/restart \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. WebSocket Connection

```javascript
const token = "your_jwt_token";
const ws = new WebSocket(`ws://localhost:9000/api/v1/logs/ws/CONTAINER_ID?token=${token}`);

ws.onmessage = (event) => {
  console.log("Log:", event.data);
};
```

### 4. MCP Connection

Configure your AI assistant (Claude Desktop, Cursor, etc.) with the MCP server URL:

```json
{
  "mcpServers": {
    "docker-agent": {
      "url": "http://localhost:9000/mcp/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

Or use the API key as a query parameter:

```
http://localhost:9000/mcp/sse?api_key=YOUR_MCP_API_KEY
```

---

## MCP Deployment Notes

### ✅ Works With

| Environment                          | Status |
|--------------------------------------|--------|
| Single instance deployment           | ✅      |
| Cloud VMs (EC2, DigitalOcean, etc.)  | ✅      |
| Kubernetes (1 replica)               | ✅      |
| Docker Compose (single container)    | ✅      |

### ⚠️ Limitations

| Environment                          | Issue                                        |
|--------------------------------------|----------------------------------------------|
| Horizontal scaling (multiple replicas) | SSE sessions are stored in-memory; needs sticky sessions |
| Serverless (Lambda, Vercel Functions)  | SSE requires long-lived connections          |
| Some load balancers                    | May timeout idle SSE connections (30-60s)    |

### Workarounds

- **Sticky Sessions**: Configure your load balancer to route the same client to the same instance
- **Single Replica**: Deploy with `replicas: 1` if horizontal scaling isn't needed
- **Increase Timeouts**: Configure load balancer idle timeout > expected connection duration

---

## Future TODOs

- [ ] Add `StreamableHTTP` transport for stateless MCP (better scaling support)
- [ ] Redis-backed session store for multi-instance deployments
- [ ] MCP tool for `docker exec` commands
- [ ] MCP tool for pulling images
- [ ] MCP tool for creating/removing containers
- [ ] MCP prompts and resources support

---

## Security & Observability

| Feature | Description |
|---------|-------------|
| **API Versioning** | All endpoints prefixed with `/api/v1` for future compatibility |
| **JWT Auth** | Tokens expire after 30 minutes (configurable) |
| **Rate Limiting** | Auth: 5/min, Actions: 10/min, Reads: 60/min |
| **CORS** | Configurable allowed origins |
| **Request Tracing** | Every response includes `X-Request-ID` and `X-Process-Time` headers |
| **Structured Logging** | JSON logs in production, colored output in debug mode |
| **Non-root Container** | Runs as `dockeragent` user |
| **No Stack Traces** | Errors don't leak internal details |
| **Health Checks** | Basic (`/healthz`) and enhanced (`/health`) endpoints |
