"""Resource usage polling task.

Polls Incus every 5 seconds for CPU/memory/disk stats of all running instances
and publishes ResourceUsageUpdated D-Bus signals + synthetic events to the EventBus.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .events import EventBus
from .incus.client import IncusClient

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 5  # seconds


async def poll_resource_usage(incus: IncusClient, bus: EventBus) -> None:
    """Run forever, emitting resource usage events every POLL_INTERVAL seconds."""
    while True:
        try:
            instances = await incus.list_instances()
            for inst in instances:
                if inst.get("status") != "Running":
                    continue
                name    = inst.get("name", "")
                project = inst.get("project", "default")
                state   = inst.get("state", {})
                if not state:
                    # Fetch full state if not included in list response
                    try:
                        detail = await incus.get_instance(name, project=project)
                        state  = detail.get("state", {})
                    except Exception:
                        continue

                cpu_usage   = _parse_cpu(state)
                mem_bytes   = _parse_memory(state)
                disk_bytes  = _parse_disk(state)

                event: dict[str, Any] = {
                    "type":      "resource_usage",
                    "project":   project,
                    "timestamp": "",
                    "metadata": {
                        "name":               name,
                        "cpu_usage":          cpu_usage,
                        "memory_usage_bytes": mem_bytes,
                        "disk_usage_bytes":   disk_bytes,
                    },
                }
                await bus.publish(event)

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.debug("Resource poll error: %s", exc)

        await asyncio.sleep(_POLL_INTERVAL)


def _parse_cpu(state: dict[str, Any]) -> float:
    """Return CPU usage as a 0.0–1.0 fraction from Incus state."""
    cpu = state.get("cpu", {})
    usage = cpu.get("usage", 0)  # nanoseconds total
    # Incus doesn't give instantaneous %; return normalised total for now.
    # A proper implementation would diff two samples.
    return min(float(usage) / 1e11, 1.0) if usage else 0.0


def _parse_memory(state: dict[str, Any]) -> int:
    mem = state.get("memory", {})
    return int(mem.get("usage", 0))


def _parse_disk(state: dict[str, Any]) -> int:
    disk = state.get("disk", {})
    total = 0
    for dev in disk.values():
        total += int(dev.get("usage", 0))
    return total
