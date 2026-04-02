"""Async Incus REST API client.

Wraps the Incus Unix socket or HTTPS endpoint.
All methods return parsed dicts/lists; callers handle serialisation.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

import httpx


# Default local Incus socket path
_INCUS_SOCKET = "/var/lib/incus/unix.socket"


class IncusError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class IncusClient:
    """Async client for the Incus REST API."""

    def __init__(self, socket_path: str = _INCUS_SOCKET) -> None:
        transport = httpx.AsyncHTTPTransport(uds=socket_path)
        self._http = httpx.AsyncClient(
            transport=transport,
            base_url="http://incus",  # host is ignored for UDS
            timeout=30,
        )

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        resp = await self._http.request(method, path, **kwargs)
        data = resp.json()
        if resp.status_code >= 400:
            raise IncusError(resp.status_code, data.get("error", str(resp.status_code)))
        # Incus wraps responses: {"type": "sync", "metadata": ...}
        return data.get("metadata", data)

    async def get(self, path: str, **kwargs: Any) -> Any:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> Any:
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> Any:
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> Any:
        return await self._request("DELETE", path, **kwargs)

    # ── Instances ─────────────────────────────────────────────────────────

    async def list_instances(self, project: str = "", remote: str = "",
                              type_filter: str = "") -> list[dict[str, Any]]:
        params: dict[str, str] = {"recursion": "1"}
        if project:
            params["project"] = project
        if type_filter:
            params["type"] = type_filter
        return await self.get("/1.0/instances", params=params)  # type: ignore[return-value]

    async def get_instance(self, name: str, project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.get(f"/1.0/instances/{name}", params=params)  # type: ignore[return-value]

    async def create_instance(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/1.0/instances", json=config)  # type: ignore[return-value]

    async def delete_instance(self, name: str, project: str = "",
                               force: bool = False) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if project:
            params["project"] = project
        if force:
            params["force"] = "1"
        return await self.delete(f"/1.0/instances/{name}", params=params)  # type: ignore[return-value]

    async def change_instance_state(self, name: str, action: str,
                                     force: bool = False, timeout: int = 30,
                                     project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.put(  # type: ignore[return-value]
            f"/1.0/instances/{name}/state",
            json={"action": action, "force": force, "timeout": timeout},
            params=params,
        )

    async def rename_instance(self, name: str, new_name: str,
                               project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.post(  # type: ignore[return-value]
            f"/1.0/instances/{name}",
            json={"name": new_name},
            params=params,
        )

    async def get_instance_logs(self, name: str, project: str = "") -> str:
        params = {"project": project} if project else {}
        resp = await self._http.get(f"/1.0/instances/{name}/logs", params=params)
        return resp.text

    # ── Snapshots ─────────────────────────────────────────────────────────

    async def list_snapshots(self, name: str, project: str = "") -> list[dict[str, Any]]:
        params: dict[str, str] = {"recursion": "1"}
        if project:
            params["project"] = project
        return await self.get(f"/1.0/instances/{name}/snapshots", params=params)  # type: ignore[return-value]

    async def create_snapshot(self, name: str, snapshot: str,
                               stateful: bool = False, project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.post(  # type: ignore[return-value]
            f"/1.0/instances/{name}/snapshots",
            json={"name": snapshot, "stateful": stateful},
            params=params,
        )

    async def delete_snapshot(self, name: str, snapshot: str,
                               project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.delete(f"/1.0/instances/{name}/snapshots/{snapshot}", params=params)  # type: ignore[return-value]

    # ── Networks ──────────────────────────────────────────────────────────

    async def list_networks(self, project: str = "") -> list[dict[str, Any]]:
        params: dict[str, str] = {"recursion": "1"}
        if project:
            params["project"] = project
        return await self.get("/1.0/networks", params=params)  # type: ignore[return-value]

    async def create_network(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/1.0/networks", json=config)  # type: ignore[return-value]

    async def get_network(self, name: str, project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.get(f"/1.0/networks/{name}", params=params)  # type: ignore[return-value]

    async def update_network(self, name: str, config: dict[str, Any],
                              project: str = "") -> None:
        params = {"project": project} if project else {}
        await self.put(f"/1.0/networks/{name}", json=config, params=params)

    async def delete_network(self, name: str, project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.delete(f"/1.0/networks/{name}", params=params)  # type: ignore[return-value]

    # ── Storage ───────────────────────────────────────────────────────────

    async def list_storage_pools(self) -> list[dict[str, Any]]:
        return await self.get("/1.0/storage-pools", params={"recursion": "1"})  # type: ignore[return-value]

    async def create_storage_pool(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/1.0/storage-pools", json=config)  # type: ignore[return-value]

    async def get_storage_pool(self, name: str) -> dict[str, Any]:
        return await self.get(f"/1.0/storage-pools/{name}")  # type: ignore[return-value]

    async def delete_storage_pool(self, name: str) -> dict[str, Any]:
        return await self.delete(f"/1.0/storage-pools/{name}")  # type: ignore[return-value]

    async def list_storage_volumes(self, pool: str,
                                    project: str = "") -> list[dict[str, Any]]:
        params: dict[str, str] = {"recursion": "1"}
        if project:
            params["project"] = project
        return await self.get(f"/1.0/storage-pools/{pool}/volumes", params=params)  # type: ignore[return-value]

    async def create_storage_volume(self, pool: str,
                                     config: dict[str, Any]) -> dict[str, Any]:
        return await self.post(f"/1.0/storage-pools/{pool}/volumes", json=config)  # type: ignore[return-value]

    async def delete_storage_volume(self, pool: str, name: str,
                                     project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.delete(  # type: ignore[return-value]
            f"/1.0/storage-pools/{pool}/volumes/custom/{name}", params=params
        )

    # ── Images ────────────────────────────────────────────────────────────

    async def list_images(self) -> list[dict[str, Any]]:
        return await self.get("/1.0/images", params={"recursion": "1"})  # type: ignore[return-value]

    async def pull_image(self, remote: str, image: str,
                          alias: str = "") -> dict[str, Any]:
        payload: dict[str, Any] = {
            "source": {"type": "image", "server": remote, "alias": image},
        }
        if alias:
            payload["aliases"] = [{"name": alias}]
        return await self.post("/1.0/images", json=payload)  # type: ignore[return-value]

    async def delete_image(self, fingerprint: str) -> dict[str, Any]:
        return await self.delete(f"/1.0/images/{fingerprint}")  # type: ignore[return-value]

    # ── Profiles ──────────────────────────────────────────────────────────

    async def list_profiles(self, project: str = "") -> list[dict[str, Any]]:
        params: dict[str, str] = {"recursion": "1"}
        if project:
            params["project"] = project
        return await self.get("/1.0/profiles", params=params)  # type: ignore[return-value]

    async def create_profile(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/1.0/profiles", json=config)  # type: ignore[return-value]

    async def get_profile(self, name: str, project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.get(f"/1.0/profiles/{name}", params=params)  # type: ignore[return-value]

    async def update_profile(self, name: str, config: dict[str, Any],
                              project: str = "") -> None:
        params = {"project": project} if project else {}
        await self.put(f"/1.0/profiles/{name}", json=config, params=params)

    async def delete_profile(self, name: str, project: str = "") -> dict[str, Any]:
        params = {"project": project} if project else {}
        return await self.delete(f"/1.0/profiles/{name}", params=params)  # type: ignore[return-value]

    # ── Projects ──────────────────────────────────────────────────────────

    async def list_projects(self) -> list[dict[str, Any]]:
        return await self.get("/1.0/projects", params={"recursion": "1"})  # type: ignore[return-value]

    async def create_project(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/1.0/projects", json=config)  # type: ignore[return-value]

    async def delete_project(self, name: str) -> dict[str, Any]:
        return await self.delete(f"/1.0/projects/{name}")  # type: ignore[return-value]

    # ── Cluster ───────────────────────────────────────────────────────────

    async def list_cluster_members(self) -> list[dict[str, Any]]:
        return await self.get("/1.0/cluster/members", params={"recursion": "1"})  # type: ignore[return-value]

    async def delete_cluster_member(self, name: str) -> dict[str, Any]:
        return await self.delete(f"/1.0/cluster/members/{name}")  # type: ignore[return-value]

    async def evacuate_cluster_member(self, name: str) -> dict[str, Any]:
        return await self.post(f"/1.0/cluster/members/{name}/state",  # type: ignore[return-value]
                               json={"action": "evacuate"})

    async def restore_cluster_member(self, name: str) -> dict[str, Any]:
        return await self.post(f"/1.0/cluster/members/{name}/state",  # type: ignore[return-value]
                               json={"action": "restore"})

    # ── Operations ────────────────────────────────────────────────────────

    async def list_operations(self) -> list[dict[str, Any]]:
        return await self.get("/1.0/operations", params={"recursion": "1"})  # type: ignore[return-value]

    async def cancel_operation(self, op_id: str) -> None:
        await self.delete(f"/1.0/operations/{op_id}")

    # ── Event stream ──────────────────────────────────────────────────────

    async def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        """Yield parsed Incus events from the event stream indefinitely."""
        async with self._http.stream("GET", "/1.0/events") as resp:
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    async def aclose(self) -> None:
        await self._http.aclose()
