import asyncio
import json
from typing import Optional, Generator, Any
from datetime import datetime, timezone

import docker
from docker.errors import NotFound, APIError, DockerException
from docker.models.containers import Container

from app.core.logging import get_logger
from app.schemas.containers import ContainerSummary
from app.schemas.stats import ContainerStats, ContainerStatsStream
from app.schemas.images import ImageSummary
from app.schemas.system import VersionResponse

logger = get_logger(__name__)

# Docker client singleton
_client: Optional[docker.DockerClient] = None


def get_client() -> docker.DockerClient:
    """Get or create Docker client with connection validation."""
    global _client
    if _client is None:
        try:
            _client = docker.from_env()
            _client.ping()
            logger.info("docker_client_connected")
        except DockerException as e:
            logger.error("docker_client_connection_failed", error=str(e))
            raise
    return _client


def close_client() -> None:
    """Close Docker client connection."""
    global _client
    if _client is not None:
        try:
            _client.close()
            logger.info("docker_client_closed")
        except Exception as e:
            logger.warning("docker_client_close_error", error=str(e))
        finally:
            _client = None


def is_connected() -> bool:
    """Check if Docker daemon is reachable."""
    try:
        get_client().ping()
        return True
    except Exception:
        return False


def list_containers(all: bool = True) -> list[ContainerSummary]:
    """List all containers with summary information."""
    client = get_client()
    containers = client.containers.list(all=all)

    result = []
    for c in containers:
        try:
            # Extract port mappings
            ports = []
            for port_str, mappings in (c.attrs.get("NetworkSettings", {}).get("Ports") or {}).items():
                if mappings:
                    for m in mappings:
                        container_port = int(port_str.split("/")[0])
                        protocol = port_str.split("/")[1] if "/" in port_str else "tcp"
                        ports.append({
                            "PrivatePort": container_port,
                            "PublicPort": int(m["HostPort"]) if m.get("HostPort") else None,
                            "Type": protocol,
                            "IP": m.get("HostIp"),
                        })

            result.append(ContainerSummary(
                id=c.short_id,
                name=c.name,
                image=c.image.tags[0] if c.image.tags else c.image.short_id,
                status=c.status,
                state=c.attrs.get("State", {}).get("Status", "unknown"),
                created=_parse_timestamp(c.attrs.get("Created", 0)),
                ports=ports,
            ))
        except Exception as e:
            logger.warning("container_parse_error", container_id=c.short_id, error=str(e))
            continue

    logger.debug("containers_listed", count=len(result), all=all)
    return result


def get_container(container_id: str) -> Container:
    """Get a container by ID or name."""
    client = get_client()
    container = client.containers.get(container_id)
    return container


def start_container(container_id: str) -> None:
    """Start a container."""
    container = get_container(container_id)
    container.start()
    logger.info("container_started", container_id=container_id)


def stop_container(container_id: str) -> None:
    """Stop a container."""
    container = get_container(container_id)
    container.stop()
    logger.info("container_stopped", container_id=container_id)


def get_logs(container_id: str, tail: int = 100) -> str:
    """Get container logs."""
    container = get_container(container_id)
    logs = container.logs(tail=tail)
    return logs.decode("utf-8", errors="replace")


def _calculate_cpu_percent(stats: dict) -> float:
    """
    Calculate CPU percentage from Docker stats.
    
    Formula: (container_delta / system_delta) * num_cpus * 100
    """
    try:
        cpu_stats = stats.get("cpu_stats", {})
        precpu_stats = stats.get("precpu_stats", {})

        cpu_delta = (
            cpu_stats.get("cpu_usage", {}).get("total_usage", 0) -
            precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
        )

        system_delta = (
            cpu_stats.get("system_cpu_usage", 0) -
            precpu_stats.get("system_cpu_usage", 0)
        )

        num_cpus = cpu_stats.get("online_cpus") or len(
            cpu_stats.get("cpu_usage", {}).get("percpu_usage", []) or [1]
        )

        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
            return round(cpu_percent, 2)
        return 0.0
    except (KeyError, TypeError, ZeroDivisionError):
        return 0.0


def _calculate_network_io(stats: dict) -> tuple[int, int]:
    """Calculate total network I/O from all interfaces."""
    networks = stats.get("networks", {})
    rx_bytes = sum(iface.get("rx_bytes", 0) for iface in networks.values())
    tx_bytes = sum(iface.get("tx_bytes", 0) for iface in networks.values())
    return rx_bytes, tx_bytes


def _calculate_block_io(stats: dict) -> tuple[int, int]:
    """Calculate block I/O from stats."""
    blkio = stats.get("blkio_stats", {}).get("io_service_bytes_recursive", []) or []
    read_bytes = sum(item.get("value", 0) for item in blkio if item.get("op") == "read")
    write_bytes = sum(item.get("value", 0) for item in blkio if item.get("op") == "write")
    return read_bytes, write_bytes


def get_container_stats(container_id: str) -> ContainerStats:
    """Get container resource statistics with correct calculations."""
    container = get_container(container_id)
    stats = container.stats(stream=False)

    mem_usage = stats.get("memory_stats", {}).get("usage", 0)
    mem_limit = stats.get("memory_stats", {}).get("limit", 1)
    mem_percent = round((mem_usage / mem_limit) * 100, 2) if mem_limit > 0 else 0.0

    cpu_percent = _calculate_cpu_percent(stats)
    network_rx, network_tx = _calculate_network_io(stats)
    block_read, block_write = _calculate_block_io(stats)

    return ContainerStats(
        container_id=container_id,
        cpu_percent=cpu_percent,
        memory_usage=mem_usage,
        memory_limit=mem_limit,
        memory_percent=mem_percent,
        network_rx=network_rx,
        network_tx=network_tx,
        block_read=block_read,
        block_write=block_write,
    )


def _parse_timestamp(value: Any) -> int:
    """Parse a timestamp value to Unix timestamp integer."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return int(dt.timestamp())
        except ValueError:
            return 0
    return 0


def list_images() -> list[ImageSummary]:
    """List all Docker images."""
    client = get_client()
    images = client.images.list()

    result = [
        ImageSummary(
            id=img.short_id,
            tags=img.tags,
            size=img.attrs.get("Size", 0),
            created=_parse_timestamp(img.attrs.get("Created", 0)),
        )
        for img in images
    ]

    logger.debug("images_listed", count=len(result))
    return result


def get_version() -> VersionResponse:
    """Get Docker version information."""
    client = get_client()
    version = client.version()

    return VersionResponse(
        api_version=version.get("ApiVersion", "unknown"),
        docker_version=version.get("Version", "unknown"),
        os=version.get("Os", ""),
        arch=version.get("Arch", ""),
    )


async def stream_logs(container_id: str) -> Generator[str, None, None]:
    """Stream container logs asynchronously."""
    container = get_container(container_id)
    logs = container.logs(stream=True, follow=True, tail=50)
    loop = asyncio.get_event_loop()

    logger.debug("log_stream_started", container_id=container_id)
    try:
        while True:
            line = await loop.run_in_executor(None, next, logs, None)
            if line is None:
                break
            yield line.decode("utf-8", errors="replace").strip()
    except StopIteration:
        pass
    except Exception as e:
        logger.error("log_stream_error", container_id=container_id, error=str(e))
        raise
    finally:
        logger.debug("log_stream_ended", container_id=container_id)


async def stream_events() -> Generator[str, None, None]:
    """Stream Docker events asynchronously."""
    client = get_client()
    events = client.events(decode=True)
    loop = asyncio.get_event_loop()

    logger.debug("event_stream_started")
    try:
        while True:
            event = await loop.run_in_executor(None, next, events, None)
            if event is None:
                break
            yield json.dumps(event)
    except Exception as e:
        logger.error("event_stream_error", error=str(e))
        raise
    finally:
        logger.debug("event_stream_ended")


async def stream_stats(container_id: str) -> Generator[str, None, None]:
    """Stream container stats asynchronously with correct calculations."""
    container = get_container(container_id)
    stats_stream = container.stats(stream=True, decode=True)
    loop = asyncio.get_event_loop()

    logger.debug("stats_stream_started", container_id=container_id)
    try:
        while True:
            stats = await loop.run_in_executor(None, next, stats_stream, None)
            if stats is None:
                break

            cpu_percent = _calculate_cpu_percent(stats)
            mem_usage = stats.get("memory_stats", {}).get("usage", 0)
            mem_limit = stats.get("memory_stats", {}).get("limit", 1)
            mem_percent = round((mem_usage / mem_limit) * 100, 2) if mem_limit > 0 else 0.0

            result = ContainerStatsStream(
                cpu_percent=cpu_percent,
                memory_usage=mem_usage,
                memory_percent=mem_percent,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            yield result.model_dump_json()
    except Exception as e:
        logger.error("stats_stream_error", container_id=container_id, error=str(e))
        raise
    finally:
        logger.debug("stats_stream_ended", container_id=container_id)
