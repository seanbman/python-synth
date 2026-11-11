"""The user-facing parameter catalogue for the Synthepyzer UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParameterSpec:
    key: str
    label: str
    control: str = "dial"
    minimum: float = 0.0
    maximum: float = 1.0
    default: Any = 0.0
    step: float = 0.01
    display: str = "number"
    choices: tuple[tuple[str, str], ...] = ()

    def path(self, layer_index: int | None = None) -> tuple[str, ...]:
        if layer_index is None:
            return ("global", self.key)
        return ("layers", str(layer_index), *self.key.split("."))


def _choices(*values: str) -> tuple[tuple[str, str], ...]:
    return tuple((value, value.replace("_", " ").title()) for value in values)


LAYER_UTILITY = (
    ParameterSpec("enabled", "Enabled", "toggle", default=True, display="toggle"),
    ParameterSpec("level", "Level", maximum=1.0, default=1.0, display="percent"),
    ParameterSpec("pan", "Pan", minimum=-1.0, maximum=1.0, default=0.0, display="pan"),
    ParameterSpec("transpose", "Transpose", "spin", minimum=-24, maximum=24, default=0, step=1, display="semitones"),
    ParameterSpec("mute", "Mute", "toggle", default=False, display="toggle"),
    ParameterSpec("solo", "Solo", "toggle", default=False, display="toggle"),
)

OSCILLATOR = (
    ParameterSpec("waveform", "Waveform", "combo", choices=_choices("sine", "triangle", "saw", "square", "noise")),
    ParameterSpec("octave", "Octave", "spin", minimum=-3, maximum=3, default=0, step=1, display="octaves"),
    ParameterSpec("semitone", "Semitone", "spin", minimum=-12, maximum=12, default=0, step=1, display="semitones"),
    ParameterSpec("fine", "Fine", maximum=1.0, minimum=-1.0, default=0.0, display="cents"),
    ParameterSpec("level", "Level", maximum=1.0, default=0.8, display="percent"),
)

MIXER = (
    ParameterSpec("mixer.osc1_level", "Oscillator 1", maximum=1.0, default=0.8, display="percent"),
    ParameterSpec("mixer.osc2_level", "Oscillator 2", maximum=1.0, default=0.0, display="percent"),
    ParameterSpec("mixer.mix", "Mix", minimum=-1.0, maximum=1.0, default=0.0, display="pan"),
)

FILTER = (
    ParameterSpec("filter.type", "Type", "combo", choices=_choices("lowpass", "highpass", "bandpass", "notch")),
    ParameterSpec("filter.cutoff", "Cutoff", maximum=1.0, default=0.72, display="percent"),
    ParameterSpec("filter.resonance", "Resonance", maximum=1.0, default=0.12, display="percent"),
    ParameterSpec("filter.key_track", "Key Track", maximum=1.0, default=0.5, display="percent"),
    ParameterSpec("filter.env_amount", "Env Amount", minimum=-1.0, maximum=1.0, default=0.25, display="percent"),
)

AMP_ENVELOPE = (
    ParameterSpec("amp_envelope.attack", "Attack", maximum=10.0, default=0.01, display="seconds", step=0.01),
    ParameterSpec("amp_envelope.decay", "Decay", maximum=10.0, default=0.35, display="seconds", step=0.01),
    ParameterSpec("amp_envelope.sustain", "Sustain", maximum=1.0, default=0.72, display="percent"),
    ParameterSpec("amp_envelope.release", "Release", maximum=10.0, default=0.25, display="seconds", step=0.01),
)

LFO = (
    ParameterSpec("lfo.shape", "Shape", "combo", choices=_choices("sine", "triangle", "saw", "square")),
    ParameterSpec("lfo.rate", "Rate", maximum=20.0, default=0.3, display="hertz", step=0.01),
    ParameterSpec("lfo.depth", "Depth", minimum=-1.0, maximum=1.0, default=0.0, display="percent"),
    ParameterSpec("lfo.destination", "Destination", "combo", choices=_choices("filter", "pitch", "amplitude")),
)

MASTER = (
    ParameterSpec("volume", "Volume", maximum=1.0, default=0.8, display="percent"),
    ParameterSpec("pan", "Pan", minimum=-1.0, maximum=1.0, default=0.0, display="pan"),
)


def format_value(value: Any, spec: ParameterSpec) -> str:
    if spec.display == "toggle":
        return "On" if value else "Off"
    if spec.display == "percent":
        return f"{float(value) * 100:.0f}%"
    if spec.display == "pan":
        number = float(value)
        return "C" if abs(number) < 0.005 else f"{number:+.2f}"
    if spec.display == "seconds":
        return f"{float(value):.2f}s"
    if spec.display == "hertz":
        return f"{float(value):.2f} Hz"
    if spec.display in {"octaves", "semitones", "cents"}:
        return f"{float(value):+.0f} {spec.display}" if float(value) else f"0 {spec.display}"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
