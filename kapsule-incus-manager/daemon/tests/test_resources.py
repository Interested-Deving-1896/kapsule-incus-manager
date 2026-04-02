"""Tests for resource usage parsing helpers."""

from kim.resources import _parse_cpu, _parse_memory, _parse_disk


def test_parse_cpu_zero_when_empty() -> None:
    assert _parse_cpu({}) == 0.0


def test_parse_cpu_normalises_nanoseconds() -> None:
    # 1e10 ns → 0.1 (10%)
    result = _parse_cpu({"cpu": {"usage": int(1e10)}})
    assert abs(result - 0.1) < 0.001


def test_parse_cpu_clamps_to_one() -> None:
    result = _parse_cpu({"cpu": {"usage": int(1e15)}})
    assert result == 1.0


def test_parse_memory_zero_when_empty() -> None:
    assert _parse_memory({}) == 0


def test_parse_memory_returns_bytes() -> None:
    assert _parse_memory({"memory": {"usage": 536870912}}) == 536870912


def test_parse_disk_zero_when_empty() -> None:
    assert _parse_disk({}) == 0


def test_parse_disk_sums_all_devices() -> None:
    state = {"disk": {"root": {"usage": 1000}, "data": {"usage": 2000}}}
    assert _parse_disk(state) == 3000


def test_parse_disk_single_device() -> None:
    state = {"disk": {"root": {"usage": 5000}}}
    assert _parse_disk(state) == 5000
