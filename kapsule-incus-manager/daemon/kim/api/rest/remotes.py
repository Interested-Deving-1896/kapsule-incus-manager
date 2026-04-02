"""Remote server management.

Remotes are stored in a local config file (not in Incus itself).
The daemon maintains its own remotes registry.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["remotes"])

_REMOTES_FILE = pathlib.Path.home() / ".config" / "kim" / "remotes.json"


def _load() -> dict[str, Any]:
    if _REMOTES_FILE.exists():
        return json.loads(_REMOTES_FILE.read_text())
    return {}


def _save(remotes: dict[str, Any]) -> None:
    _REMOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    _REMOTES_FILE.write_text(json.dumps(remotes, indent=2))


@router.get("/remotes")
async def list_remotes() -> Any:
    return list(_load().values())


@router.post("/remotes", status_code=201)
async def add_remote(body: dict[str, Any]) -> Any:
    remotes = _load()
    name = body["name"]
    if name in remotes:
        raise HTTPException(409, f"Remote '{name}' already exists")
    remotes[name] = body
    _save(remotes)
    return body


@router.get("/remotes/{name}")
async def get_remote(name: str) -> Any:
    remotes = _load()
    if name not in remotes:
        raise HTTPException(404, f"Remote '{name}' not found")
    return remotes[name]


@router.delete("/remotes/{name}", status_code=204)
async def remove_remote(name: str) -> None:
    remotes = _load()
    if name not in remotes:
        raise HTTPException(404, f"Remote '{name}' not found")
    del remotes[name]
    _save(remotes)
