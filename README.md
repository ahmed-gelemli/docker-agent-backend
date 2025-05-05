# 🚀 Docker Agent Backend

A lightweight, secure, and extensible backend agent built with **FastAPI** that lets you manage and monitor Docker containers remotely — via both **REST APIs** and **real-time WebSocket streaming**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## 🔧 Features

✅ List Docker containers  
✅ View logs  
✅ Start / stop containers  
✅ Real-time log streaming via WebSocket  
✅ Stream live container stats  
✅ Docker events stream (start/stop/etc)  
✅ List images  
✅ Secure token-based authentication  
✅ Easy deployment via Docker or Docker Compose  

---

## 📦 API Overview

### 🔐 Auth (Token Required via `Authorization: Bearer <token>`)

| Method | Endpoint                         | Description                  |
|--------|----------------------------------|------------------------------|
| GET    | `/auth/check`                    | Validate auth token          |

---

### 📦 Containers

| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| GET    | `/containers/`                    | List containers          |
| GET    | `/containers/{id}/logs`           | View container logs      |
| POST   | `/containers/{id}/start`          | Start container          |
| POST   | `/containers/{id}/stop`           | Stop container           |

---

### 📊 Stats & System Info

| Method | Endpoint                          | Description                 |
|--------|-----------------------------------|-----------------------------|
| GET    | `/stats/{container_id}`           | CPU and memory stats        |
| GET    | `/version`                        | Docker & API version        |
| GET    | `/healthz`                        | Health check (no auth)      |

---

### 🖼️ Images

| Method | Endpoint                          | Description                 |
|--------|-----------------------------------|-----------------------------|
| GET    | `/images/`                        | List available Docker images |

---

### 🔌 WebSocket Endpoints (Real-time, secured with `?token=` query param)

| WS Path                                | Description                        |
|----------------------------------------|------------------------------------|
| `/logs/ws/{container_id}`              | Stream live logs                   |
| `/stats/ws/{container_id}`             | Stream live CPU/memory stats       |
| `/events/ws`                           | Stream Docker events (create, die) |

---

## ⚙️ Installation

### 🐳 Using Docker Compose

```bash
# Clone the repo
git clone https://github.com/yourusername/docker-agent-backend.git
cd docker-agent-backend

# Set your token
echo "API_TOKEN=your_secure_token" > .env

# Build and run
docker compose up --build -d
