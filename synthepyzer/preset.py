"""Versioned, forward-compatible Synthepyzer preset files."""

from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from .state import CURRENT_ENGINE_VERSION, default_layer, default_preset_state

PRESET_FORMAT = "spyzr"
PRESET_SUFFIX = ".spyzr"
CURRENT_FORMAT_VERSION = 1


class PresetError(ValueError):
    """Base error for invalid or unusable preset files."""


class PresetFormatError(PresetError):
    """Raised when a preset has invalid structure or JSON."""


class PresetVersionError(PresetError):
    """Raised when a preset comes from a newer unsupported format."""


def default_preset(name: str = "Init Patch") -> dict[str, Any]:
    """Return a complete preset with the requested display name."""
    payload = default_preset_state()
    payload["meta"]["name"] = name
    return payload


def _ensure_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PresetFormatError(f"Preset field '{field}' must be an object")
    return value


def _migrate_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Wrap the original single-layer shape in the v1 two-layer structure."""
    migrated = deepcopy(payload)
    legacy_layer = migrated.pop("layer", None)
    if legacy_layer is None:
        legacy_layer = default_layer("A")
    else:
        legacy_layer = _ensure_dict(legacy_layer, "layer")
        legacy_layer.setdefault("id", "A")
        legacy_layer["id"] = "A"

    layer_b = default_layer("B")
    layer_b["enabled"] = False
    migrated.setdefault("meta", deepcopy(default_preset()["meta"]))
    migrated.setdefault("global", deepcopy(default_preset()["global"]))
    migrated["layers"] = [legacy_layer, layer_b]
    migrated["format"] = PRESET_FORMAT
    migrated["format_version"] = 1
    migrated.setdefault("product", "Synthepyzer")
    migrated.setdefault("engine_version", CURRENT_ENGINE_VERSION)
    return migrated


def migrate_preset(payload: dict[str, Any]) -> dict[str, Any]:
    """Migrate a payload to the current version without dropping unknown data."""
    migrated = deepcopy(_ensure_dict(payload, "root"))
    version = migrated.get("format_version", 0)
    if not isinstance(version, int) or isinstance(version, bool):
        raise PresetFormatError("Preset field 'format_version' must be an integer")
    if version > CURRENT_FORMAT_VERSION:
        raise PresetVersionError(
            f"Preset format {version} is newer than supported format {CURRENT_FORMAT_VERSION}"
        )
    if version == 0:
        migrated = _migrate_v0(migrated)
    return migrated


def validate_preset(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the current contract while retaining all extra fields."""
    data = _ensure_dict(payload, "root")
    if data.get("format") != PRESET_FORMAT:
        raise PresetFormatError("This file is not a Synthepyzer .spyzr preset")
    version = data.get("format_version")
    if version != CURRENT_FORMAT_VERSION:
        raise PresetVersionError(f"Unsupported preset format version: {version}")
    _ensure_dict(data.get("meta"), "meta")
    _ensure_dict(data.get("global"), "global")
    layers = data.get("layers")
    if not isinstance(layers, list):
        raise PresetFormatError("Preset field 'layers' must be an array")

    ids = []
    for layer in layers:
        layer_data = _ensure_dict(layer, "layers[]")
        layer_id = layer_data.get("id")
        if not isinstance(layer_id, str) or not layer_id:
            raise PresetFormatError("Every layer must have a non-empty string id")
        if layer_id in ids:
            raise PresetFormatError(f"Duplicate layer id: {layer_id}")
        ids.append(layer_id)
    missing = {"A", "B"}.difference(ids)
    if missing:
        raise PresetFormatError(f"Preset is missing required layer(s): {', '.join(sorted(missing))}")
    return data


def load_preset(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load, migrate, and validate one .spyzr preset."""
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except FileNotFoundError as exc:
        raise PresetFormatError(f"Preset not found: {source}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PresetFormatError(f"Could not read preset '{source}': {exc}") from exc
    return validate_preset(migrate_preset(payload))


def save_preset(path: str | os.PathLike[str], payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and atomically save a preset, preserving unknown fields."""
    normalized = validate_preset(migrate_preset(payload))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(encoded)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, target)
    except OSError as exc:
        raise PresetFormatError(f"Could not save preset '{target}': {exc}") from exc
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
    return normalized
