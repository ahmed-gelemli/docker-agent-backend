from mcp.server import Server
from mcp.types import Tool, TextContent

from app.services import docker_service
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create MCP server instance
mcp_server = Server("docker-agent")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="docker_health",
            description="Get Docker daemon health status and system information including container counts, memory, and CPU info",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="docker_version",
            description="Get Docker version information",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="list_containers",
            description="List all Docker containers with their status, image, and port information",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Include stopped containers (default: true)",
                        "default": True,
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_container",
            description="Get detailed information about a specific container including config, state, mounts, and networks",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name",
                    }
                },
                "required": ["container_id"],
            },
        ),
        Tool(
            name="get_container_logs",
            description="Get logs from a specific container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name",
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to return from the end (default: 100)",
                        "default": 100,
                    },
                },
                "required": ["container_id"],
            },
        ),
        Tool(
            name="get_container_stats",
            description="Get resource usage statistics (CPU, memory, network, block I/O) for a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name",
                    }
                },
                "required": ["container_id"],
            },
        ),
        Tool(
            name="list_images",
            description="List all Docker images with their tags and sizes",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="start_container",
            description="Start a stopped container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name",
                    }
                },
                "required": ["container_id"],
            },
        ),
        Tool(
            name="stop_container",
            description="Stop a running container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name",
                    }
                },
                "required": ["container_id"],
            },
        ),
        Tool(
            name="restart_container",
            description="Restart a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds before killing the container (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["container_id"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    logger.debug("mcp_tool_called", tool=name, arguments=arguments)

    try:
        if name == "docker_health":
            result = docker_service.get_system_info()

        elif name == "docker_version":
            version = docker_service.get_version()
            result = version.model_dump()

        elif name == "list_containers":
            include_all = arguments.get("all", True)
            containers = docker_service.list_containers(all=include_all)
            result = [c.model_dump() for c in containers]

        elif name == "get_container":
            container_id = arguments["container_id"]
            result = docker_service.get_container_details(container_id)

        elif name == "get_container_logs":
            container_id = arguments["container_id"]
            tail = arguments.get("tail", 100)
            result = docker_service.get_logs(container_id, tail=tail)

        elif name == "get_container_stats":
            container_id = arguments["container_id"]
            stats = docker_service.get_container_stats(container_id)
            result = stats.model_dump()

        elif name == "list_images":
            images = docker_service.list_images()
            result = [img.model_dump() for img in images]

        elif name == "start_container":
            container_id = arguments["container_id"]
            docker_service.start_container(container_id)
            result = {"status": "started", "container_id": container_id}

        elif name == "stop_container":
            container_id = arguments["container_id"]
            docker_service.stop_container(container_id)
            result = {"status": "stopped", "container_id": container_id}

        elif name == "restart_container":
            container_id = arguments["container_id"]
            timeout = arguments.get("timeout", 10)
            docker_service.restart_container(container_id, timeout=timeout)
            result = {"status": "restarted", "container_id": container_id}

        else:
            logger.warning("mcp_unknown_tool", tool=name)
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        # Convert result to string for text content
        import json
        text_result = json.dumps(result, indent=2, default=str)
        logger.debug("mcp_tool_success", tool=name)
        return [TextContent(type="text", text=text_result)]

    except Exception as e:
        logger.error("mcp_tool_error", tool=name, error=str(e))
        return [TextContent(type="text", text=f"Error: {str(e)}")]

