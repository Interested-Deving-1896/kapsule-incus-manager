"""CLI command tests using Click's test runner and httpx mock transport."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
from click.testing import CliRunner

from kim.cli.main import cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(data: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        content=json.dumps(data).encode(),
        headers={"content-type": "application/json"},
    )


def _runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


def _invoke(args: list[str], mock_data: Any = None, status_code: int = 200):
    """Invoke CLI with a mocked DaemonClient that returns *mock_data*."""
    runner = _runner()
    mock_resp = _mock_response(mock_data or [], status_code)

    with patch("kim.cli.client.httpx.Client") as MockClient:
        mock_http = MagicMock()
        mock_http.get.return_value = mock_resp
        mock_http.post.return_value = mock_resp
        mock_http.put.return_value = mock_resp
        mock_http.delete.return_value = mock_resp
        MockClient.return_value = mock_http
        result = runner.invoke(cli, args, catch_exceptions=False)

    return result, mock_http


# ---------------------------------------------------------------------------
# container list
# ---------------------------------------------------------------------------

def test_container_list_calls_instances_endpoint() -> None:
    result, mock_http = _invoke(["container", "list"], mock_data=[])
    assert result.exit_code == 0
    mock_http.get.assert_called_once()
    call_args = mock_http.get.call_args
    assert "/api/v1/instances" in call_args[0][0]


def test_container_list_passes_type_container() -> None:
    _, mock_http = _invoke(["container", "list"])
    params = mock_http.get.call_args[1].get("params", {})
    assert params.get("type") == "container"


def test_container_list_passes_project_option() -> None:
    _, mock_http = _invoke(["container", "list", "--project", "myproject"])
    params = mock_http.get.call_args[1].get("params", {})
    assert params.get("project") == "myproject"


# ---------------------------------------------------------------------------
# container create
# ---------------------------------------------------------------------------

def test_container_create_posts_to_instances() -> None:
    result, mock_http = _invoke(
        ["container", "create", "mybox", "--image", "images:ubuntu/24.04"],
        mock_data={"id": "op-123"},
    )
    assert result.exit_code == 0
    mock_http.post.assert_called_once()
    path = mock_http.post.call_args[0][0]
    assert "/api/v1/instances" in path


def test_container_create_sends_correct_body() -> None:
    _, mock_http = _invoke(
        ["container", "create", "mybox", "--image", "images:ubuntu/24.04",
         "--profile", "default", "--profile", "gpu"],
        mock_data={"id": "op-123"},
    )
    body = mock_http.post.call_args[1]["json"]
    assert body["name"] == "mybox"
    assert body["image"] == "images:ubuntu/24.04"
    assert body["type"] == "container"
    assert "default" in body["profiles"]
    assert "gpu" in body["profiles"]


# ---------------------------------------------------------------------------
# container start / stop / restart
# ---------------------------------------------------------------------------

def test_container_start_puts_state() -> None:
    _, mock_http = _invoke(["container", "start", "mybox"])
    mock_http.put.assert_called_once()
    path = mock_http.put.call_args[0][0]
    assert "mybox/state" in path
    body = mock_http.put.call_args[1]["json"]
    assert body["action"] == "start"


def test_container_stop_puts_state() -> None:
    _, mock_http = _invoke(["container", "stop", "mybox"])
    body = mock_http.put.call_args[1]["json"]
    assert body["action"] == "stop"


def test_container_stop_force_flag() -> None:
    _, mock_http = _invoke(["container", "stop", "--force", "mybox"])
    body = mock_http.put.call_args[1]["json"]
    assert body["force"] is True


def test_container_restart_puts_state() -> None:
    _, mock_http = _invoke(["container", "restart", "mybox"])
    body = mock_http.put.call_args[1]["json"]
    assert body["action"] == "restart"


# ---------------------------------------------------------------------------
# container delete
# ---------------------------------------------------------------------------

def test_container_delete_calls_delete() -> None:
    _, mock_http = _invoke(["container", "delete", "mybox"])
    mock_http.delete.assert_called_once()
    path = mock_http.delete.call_args[0][0]
    assert "mybox" in path


# ---------------------------------------------------------------------------
# vm list
# ---------------------------------------------------------------------------

def test_vm_list_passes_type_virtual_machine() -> None:
    _, mock_http = _invoke(["vm", "list"])
    params = mock_http.get.call_args[1].get("params", {})
    assert params.get("type") == "virtual-machine"


# ---------------------------------------------------------------------------
# network / storage / image / profile / project / cluster / remote / operation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("args,expected_path", [
    (["network", "list"],   "/api/v1/networks"),
    (["storage", "list"],   "/api/v1/storage-pools"),
    (["image", "list"],     "/api/v1/images"),
    (["profile", "list"],   "/api/v1/profiles"),
    (["project", "list"],   "/api/v1/projects"),
    (["cluster", "list"],   "/api/v1/cluster/members"),
    (["remote", "list"],    "/api/v1/remotes"),
    (["operation", "list"], "/api/v1/operations"),
])
def test_list_commands_call_correct_endpoint(args: list[str], expected_path: str) -> None:
    result, mock_http = _invoke(args, mock_data=[])
    assert result.exit_code == 0
    path = mock_http.get.call_args[0][0]
    assert expected_path in path


# ---------------------------------------------------------------------------
# operation cancel
# ---------------------------------------------------------------------------

def test_operation_cancel_calls_delete() -> None:
    _, mock_http = _invoke(["operation", "cancel", "op-abc123"])
    mock_http.delete.assert_called_once()
    path = mock_http.delete.call_args[0][0]
    assert "op-abc123" in path


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

def test_http_error_exits_nonzero() -> None:
    runner = _runner()
    error_resp = httpx.Response(
        status_code=500,
        content=b'{"error": "internal server error"}',
        headers={"content-type": "application/json"},
        request=httpx.Request("GET", "http://127.0.0.1:8765/api/v1/instances"),
    )

    with patch("kim.cli.client.httpx.Client") as MockClient:
        mock_http = MagicMock()
        mock_http.get.return_value = error_resp
        MockClient.return_value = mock_http
        result = runner.invoke(cli, ["container", "list"])

    assert result.exit_code != 0
