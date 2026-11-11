# Synthepyzer — audio engine architecture decision

Decision date: 2026-11-11. **Selected primary DSP backend: pyo 1.1.0**. Implementation is **planned**; it is not installed or active in this repo yet.

## Why pyo

pyo is a C-backed, real-time DSP library that exposes synthesis generators, tables, LFO/modulation, filters and MIDI from Python. It offers far more direct and efficient real-time building blocks for this PyQt6 synth than writing a Python sample loop or relying on a notebook/game framework.

- **pyo** — chosen primary real-time synthesis, voice graph and output-device owner. PyPI 1.1.0, released 2026-10-09; official documentation: https://belangeo.github.io/pyo/ ; PyPI: https://pypi.org/project/pyo/ . License **LGPL-3.0-or-later**: check redistribution, notices and LGPL obligations if packaging a proprietary executable.
- **NumPy** — supporting utility for deterministic offline waveform samples, FFT visual analysis and test vectors; not the audio stream callback. **SciPy** — optionally for coefficient/response analysis, not a second filter running in production. Add only as needed.
- **synthesizer** — useful as a compact education/prototype library, but less suitable than pyo as the primary mature realtime graph; keep it out of production dependency tree.
- **Supriya** — good Python control of SuperCollider synthesis, but its mandatory separate SuperCollider executable/server complicates packaging and debugging of this single-app synth; not selected.
- **Jupylet** — usable synthesis primitives, but its game/notebook-oriented architecture is a poorer fit than native PyQt6 + pyo.
- **sounddevice / PyAudio** — **not needed as a second output engine** alongside pyo. Use only if a clear measured integration need appears, after written decision.

Primary official references:
- https://pypi.org/project/pyo/
- https://belangeo.github.io/pyo/api/classes/filters.html
- https://belangeo.github.io/pyo/api/classes/tableprocess.html
- https://supriya-project.github.io/supriya/
- https://pypi.org/project/synthesizer/

## Runtime and packaging

Current pyproject.toml requires Python >=3.10 for the dependency-free model and optional Qt UI. pyo 1.1.0 currently requires Python >=3.11, so **update the app's supported/runtime Python version deliberately when activating audio**. Do not break the existing model tests or silently make pyo a hard dependency before the engine works.

Preferred optional extras, to be validated on target OS and Python:
- ui: PyQt6
- audio: pyo >=1.1,<2
- analysis/development (optional): numpy, scipy, only when used

This is one Python desktop application with a pyo Server. Do not add SuperCollider, Docker, a Node service, network backend, or a web application. Keep the core state/model importable without pyo or PyQt for tests.

## Source tree and ownership (proposed)

- synthepyzer/engine/interface.py: minimal protocol for start/stop, device enumeration, note_on/note_off, parameter updates, panic, status, and sample/response snapshots.
- synthepyzer/engine/pyo_backend.py: own pyo.Server and DSP nodes; lazy import; explicit boot/shutdown; resource cleanup; errors surfaced to status.
- synthepyzer/engine/voice.py: note/gate/velocity, oscillators and envelope per voice, deterministic allocation/stealing; no blocking allocations in an active audio callback.
- synthepyzer/engine/mapper.py: pure functions mapping existing normalized state to Hz, Q, cents, amplitudes and pan; centralized and unit tested.
- synthepyzer/engine/waves.py: offline wavetable interpolation/bounds/periodic seam validation; prepare replacement buffers off the audio thread.
- synthepyzer/widgets/waveform_editor.py and response_plot.py: Qt painting and interaction only; no direct calls to pyo in paintEvent.
- Existing StateController remains source of truth. A controller/engine bridge translates state changes into bounded coalesced engine commands.

These are suggestions for new modules, not claims that they already exist.

## Real-time signal graph

MIDI note/gate/velocity -> two independent synth **layers**:
- for each enabled, unmuted, solo-eligible layer: transpose + two tuned oscillators (sine/triangle/saw/square/noise), oscillator levels and mixer balance -> LP/HP/BP/Notch filter -> gate-aware ADSR amplifier -> per-layer level/pan;
- modulate pitch/filter/amp from the layer's LFO and supported key tracking/envelope amount;
- sum A+B -> global volume/pan -> stereo output.

Define and test when oscillator-level and mixer-level gains multiply, the meaning of the bipolar Mix control, clipping/headroom and whether solo in one layer mutes the other. No duplicate hidden gain stages. The disabled B layer must produce no sound by default.

For standard waveforms, prefer pyo generators or oscillator tables with appropriate anti-alias treatment; demonstrate aliasing and polyphony tests. For editable custom waveforms, sample the user curve to a periodic wavetable, normalize/gate appropriately, use a pyo table oscillator, and update it via a safe handoff rather than mutating a live object on the Qt paint thread.

## Filter: link controls, DSP and plot

First implementation candidate: pyo Biquad, types 0=LP, 1=HP, 2=BP, 3=bandstop (Notch), confirmed by official filter documentation. Make frequency mapping explicit, e.g. f(x)=20 * (fmax/20)^x Hz where x is stored cutoff 0..1 and fmax=min(20000, 0.45*sample_rate). Choose and test Q mapping from normalized 0..1 to pyo-supported values (e.g. 1..15); do not use a percent directly as a Q.

The response plot must be computed from **the actual chosen filter's** transfer function/coefficients, not a generic drawn slope. Its hit handle changes the same normalized parameters as the sliders. Report frequency Hz and amplitude dB only after correct mapping. Update with sample rate changes.

## LFO, envelope, MIDI and audio lifecycle

- Four supported LFO shapes, rate/depth and exact destination ("filter", "pitch", "amplitude"). Ensure zero depth has no audible effect; avoid zipper noise with parameter smoothing.
- ADSR must begin on note-on, sustain correctly until note-off, and release on note-off. Do not render fixed prerecorded clips instead of synthesizing voices.
- MIDI must handle overlapping notes/chords and independent releases, velocity, bend, mod wheel and sustain pedal; choose engine-native or separate MIDI input deliberately and avoid double-triggering.
- Boot/stop server only through explicit lifecycle; connect actual output device and report real errors. Panic stops all active voices. UI remains responsive if devices are missing.
- Qt GUI thread exclusively paints/edits; audio thread/process exclusively performs DSP. No Python-generated sample arrays per callback, no GUI work in the DSP callback, no uncontrolled thread crossing. Keep long operations off the audio thread.
- Scope graphs: waveform design preview is generated from model; **live** oscilloscope/audio/spectrum is labeled live only when fed actual engine samples.
- Show measurable status only when implemented; avoid fake CPU meters, fake output levels and fake active voice count.

## Preset migration

Existing .spyzr format version 1 is authoritative. To store a custom waveform, add a backward-compatible structure scoped to each oscillator, e.g. custom_wave with node coordinates/curve interpolation metadata; define sampling limits, closure and schema validation. Raise format_version and write a v1->v2 migration only when the feature is implemented; preserve unrelated/unknown fields and v0 migration. Round-trip tests must include A and B each having independent custom waves.

## Definition of done for first audible milestone

- A/B synth engine starts, produces a test note with actual pyo output (manual hardware check).
- Note off releases precisely; two-note chord is not mono summation artifacts.
- Both osc waveforms and filter types create audibly/measurably distinct output.
- Mute/solo/enable/layer level/global level behave predictably.
- Filter cutoff slider, graph drag and engine update reflect the same state.
- Save/reload preserves deterministic patch parameters; no output-device selection claims before supported.
- No audio or UI regressions: tests on pure models without audio hardware, offline DSP renders where pyo is available, manual recording/listening test on target Linux desktop, and no GUI thread stalls.

**Codex:** follow [CODEX_IMPLEMENTATION.md](CODEX_IMPLEMENTATION.md). Do not say "sound works" on the basis of UI tests or the presence of pyo in dependencies alone.
