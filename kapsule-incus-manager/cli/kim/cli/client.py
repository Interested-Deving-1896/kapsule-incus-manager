"""HTTP client wrapper used by CLI commands."""

from __future__ import annotations

import json
import sys
from typing import Any

import httpx
from rich.console import Console

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

    def get_text(self, path: str, **kwargs: Any) -> None:
        """Fetch a plain-text response (e.g. logs) and print to stdout."""
        resp = self._http.get(path, **kwargs)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            console.print(f"[red]Error {exc.response.status_code}:[/] {exc.response.text}")
            sys.exit(1)
        console.print(resp.text)

    def download_file(self, path: str, params: dict[str, str], dest: str) -> None:
        """Download binary content from *path* and write to *dest*."""
        resp = self._http.get(path, params=params)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            console.print(f"[red]Error {exc.response.status_code}:[/] {exc.response.text}")
            sys.exit(1)
        with open(dest, "wb") as fh:
            fh.write(resp.content)
        console.print(f"[green]Saved[/] {dest} ({len(resp.content)} bytes)")

    def upload_file(self, path: str, params: dict[str, str], src: str) -> None:
        """Read *src* and POST its bytes to *path*."""
        with open(src, "rb") as fh:
            data = fh.read()
        resp = self._http.post(
            path, params=params, content=data,
            headers={"Content-Type": "application/octet-stream"},
        )
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            console.print(f"[red]Error {exc.response.status_code}:[/] {exc.response.text}")
            sys.exit(1)
        console.print(f"[green]Uploaded[/] {src} ({len(data)} bytes)")

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
