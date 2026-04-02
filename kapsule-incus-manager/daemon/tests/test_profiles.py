"""Tests for the profile preset library."""

from kim.profiles.library import list_presets


def test_list_presets_returns_list() -> None:
    presets = list_presets()
    assert isinstance(presets, list)
    assert len(presets) > 0


def test_presets_have_required_fields() -> None:
    for preset in list_presets():
        assert "name"        in preset
        assert "description" in preset
        assert "category"    in preset
        assert "profile"     in preset


def test_preset_categories_are_known() -> None:
    known = {"gpu", "audio", "display", "rocm", "nesting", "network"}
    for preset in list_presets():
        assert preset["category"] in known, \
            f"Unknown category '{preset['category']}' in preset '{preset['name']}'"


def test_builtin_presets_include_gpu() -> None:
    names = {p["name"] for p in list_presets()}
    assert "gpu-passthrough" in names


def test_builtin_presets_include_audio() -> None:
    names = {p["name"] for p in list_presets()}
    assert "audio" in names


def test_builtin_presets_include_nesting() -> None:
    names = {p["name"] for p in list_presets()}
    assert "nesting" in names


def test_preset_profile_has_name() -> None:
    for preset in list_presets():
        assert "name" in preset["profile"], \
            f"Profile in preset '{preset['name']}' missing 'name' field"
