
import docker
import asyncio
import json

client = docker.from_env()

def list_containers(all=True):
    return client.containers.list(all=all)

def start_container(container_id):
    container = client.containers.get(container_id)
    container.start()

def stop_container(container_id):
    container = client.containers.get(container_id)
    container.stop()

def get_logs(container_id, tail=100):
    container = client.containers.get(container_id)
    return container.logs(tail=tail).decode()

def get_container_stats(container_id):
    container = client.containers.get(container_id)
    stats = container.stats(stream=False)
    return {
        "cpu_percent": stats["cpu_stats"]["cpu_usage"]["total_usage"],
        "mem_usage": stats["memory_stats"]["usage"],
        "mem_limit": stats["memory_stats"].get("limit", 0),
    }

def list_images():
    return [{"id": img.id, "tags": img.tags} for img in client.images.list()]

def get_version():
    return {
        "api_version": client.version().get("ApiVersion"),
        "docker_version": client.version().get("Version")
    }

async def stream_logs(container_id):
    container = client.containers.get(container_id)
    logs = container.logs(stream=True, follow=True)
    loop = asyncio.get_event_loop()

    while True:
        try:
            line = await loop.run_in_executor(None, next, logs, None)
            if line is None:
                break
            yield line.decode().strip()
        except StopIteration:
            break
        except Exception as e:
            yield f"Error streaming logs: {str(e)}"
            break

async def stream_events():
    events = client.events(decode=True)
    loop = asyncio.get_event_loop()
    while True:
        try:
            event = await loop.run_in_executor(None, next, events, None)
            if event is None:
                break
            yield json.dumps(event)
        except Exception as e:
            yield json.dumps({"error": str(e)})
            break

async def stream_stats(container_id):
    container = client.containers.get(container_id)
    stats_stream = container.stats(stream=True)
    loop = asyncio.get_event_loop()
    while True:
        try:
            stat = await loop.run_in_executor(None, next, stats_stream, None)
            if stat is None:
                break
            yield json.dumps({
                "cpu": stat["cpu_stats"]["cpu_usage"]["total_usage"],
                "mem": stat["memory_stats"]["usage"]
            })
        except Exception as e:
            yield json.dumps({"error": str(e)})
            break
