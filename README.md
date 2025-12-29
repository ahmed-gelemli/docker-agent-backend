# Docker Agent Backend

A lightweight, secure, and extensible backend agent built with **FastAPI** that lets you manage and monitor Docker containers remotely — via both **REST APIs** and **real-time WebSocket streaming**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## Features

- List Docker containers
- View logs
- Start / stop containers
- Real-time log streaming via WebSocket
- Stream live container stats
- Docker events stream (start/stop/etc)
- List images
- **JWT authentication** with token expiration
- **Rate limiting** to prevent abuse
- **CORS** configuration
- **Production-ready** Docker setup (non-root, health checks)

---

## API Overview

### Auth

| Method | Endpoint       | Description                     | Auth Required |
|--------|----------------|---------------------------------|---------------|
| POST   | `/auth/login`  | Get JWT token                   | No            |
| GET    | `/auth/check`  | Validate token & get user info  | Yes           |

### Containers

| Method | Endpoint                   | Description         | Rate Limit |
|--------|----------------------------|---------------------|------------|
| GET    | `/containers/`             | List containers     | 60/min     |
| GET    | `/containers/{id}/logs`    | View container logs | 60/min     |
| POST   | `/containers/{id}/start`   | Start container     | 10/min     |
| POST   | `/containers/{id}/stop`    | Stop container      | 10/min     |

### Stats & System

| Method | Endpoint              | Description          | Auth Required |
|--------|-----------------------|----------------------|---------------|
| GET    | `/stats/{id}`         | CPU and memory stats | Yes           |
| GET    | `/version`            | Docker & API version | Yes           |
| GET    | `/healthz`            | Health check         | No            |

### Images

| Method | Endpoint    | Description          |
|--------|-------------|----------------------|
| GET    | `/images/`  | List Docker images   |

### WebSocket Endpoints

Real-time streaming with JWT token passed as query parameter.

| Path                        | Description                 |
|-----------------------------|-----------------------------|
| `/logs/ws/{id}?token=JWT`   | Stream live logs            |
| `/stats/ws/{id}?token=JWT`  | Stream live CPU/memory      |
| `/events/ws?token=JWT`      | Stream Docker events        |

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

# Application (optional)
DEBUG=false
APP_NAME=Docker Agent
```

---

## Usage

### 1. Get a JWT Token

```bash
curl -X POST http://localhost:9000/auth/login \
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
curl http://localhost:9000/containers/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Start a container
curl -X POST http://localhost:9000/containers/CONTAINER_ID/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. WebSocket Connection

```javascript
const token = "your_jwt_token";
const ws = new WebSocket(`ws://localhost:9000/logs/ws/CONTAINER_ID?token=${token}`);

ws.onmessage = (event) => {
  console.log("Log:", event.data);
};
```

---

## Security Features

| Feature | Description |
|---------|-------------|
| **JWT Auth** | Tokens expire after 30 minutes (configurable) |
| **Rate Limiting** | Auth: 5/min, Actions: 10/min, Reads: 60/min |
| **CORS** | Configurable allowed origins |
| **Non-root Container** | Runs as `dockeragent` user |
| **No Stack Traces** | Errors don't leak internal details |
| **Health Checks** | Built-in Docker health check |

