"""HTTP client wrapper used by CLI commands."""

from __future__ import annotations

import json
import sys
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

console = Console()


class DaemonClient:
    def __init__(self, base_url: str) -> None:
        self._base = base_url.rstrip("/")
        self._http = httpx.Client(base_url=self._base, timeout=30)

    def _handle(self, resp: httpx.Response) -> Any:
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            console.print(f"[red]Error {exc.response.status_code}:[/] {exc.response.text}")
            sys.exit(1)
        data = resp.json()
        # Pretty-print as JSON for now; individual commands can override
        console.print_json(json.dumps(data))
        return data

    def get(self, path: str, **kwargs: Any) -> Any:
        return self._handle(self._http.get(path, **kwargs))

    def post(self, path: str, **kwargs: Any) -> Any:
        return self._handle(self._http.post(path, **kwargs))

    def put(self, path: str, **kwargs: Any) -> Any:
        return self._handle(self._http.put(path, **kwargs))

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self._handle(self._http.delete(path, **kwargs))

    def stream_events(self, event_type: str = "") -> None:
        """Stream SSE events from the daemon, printing each to stdout."""
        params = {"type": event_type} if event_type else {}
        with self._http.stream("GET", "/api/v1/events", params=params) as resp:
            for line in resp.iter_lines():
                if line.startswith("data:"):
                    payload = line[5:].strip()
                    try:
                        console.print_json(payload)
                    except Exception:
                        console.print(payload)
