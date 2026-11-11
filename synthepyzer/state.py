"""The dependency-free Synthepyzer instrument state model.

The UI and DSP layers can consume this structure without having to know about
the preset file format. Parameter names intentionally match the manual.
"""

from copy import deepcopy

CURRENT_ENGINE_VERSION = "0.1.0"


def default_oscillator():
    return {
        "waveform": "saw",
        "octave": 0,
        "semitone": 0,
        "fine": 0.0,
        "level": 0.8,
    }


def default_layer(layer_id):
    """Return a fresh, independently editable layer state."""
    return {
        "id": layer_id,
        "enabled": layer_id == "A",
        "level": 1.0,
        "pan": 0.0,
        "transpose": 0,
        "mute": False,
        "solo": False,
        "oscillators": {
            "osc1": default_oscillator(),
            "osc2": {
                **default_oscillator(),
                "waveform": "triangle",
                "octave": -1,
                "level": 0.0,
            },
        },
        "mixer": {
            "osc1_level": 0.8,
            "osc2_level": 0.0,
            "mix": 0.0,
        },
        "filter": {
            "type": "lowpass",
            "cutoff": 0.72,
            "resonance": 0.12,
            "key_track": 0.5,
            "env_amount": 0.25,
        },
        "amp_envelope": {
            "attack": 0.01,
            "decay": 0.35,
            "sustain": 0.72,
            "release": 0.25,
        },
        "lfo": {
            "shape": "sine",
            "rate": 0.3,
            "depth": 0.0,
            "destination": "filter",
        },
    }


def default_preset_state():
    """Return a new complete two-layer state suitable for a new patch."""
    return {
        "format": "spyzr",
        "format_version": 1,
        "product": "Synthepyzer",
        "engine_version": CURRENT_ENGINE_VERSION,
        "meta": {
            "name": "Init Patch",
            "author": "",
            "tags": [],
            "created_at": "",
            "modified_at": "",
        },
        "global": {
            "volume": 0.8,
            "pan": 0.0,
        },
        "layers": [default_layer("A"), default_layer("B")],
    }


def clone_state(state):
    """Make a deep copy before applying edits or serializing a patch."""
    return deepcopy(state)
