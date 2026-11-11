# Synthepyzer — feature and implementation truth audit

Reviewed against current main branch (2026-11-11). Source-of-truth files: synthepyzer/{main_window,panels,controls,parameters,binding,state,preset}.py and tests/. Read these files before editing. This audit distinguishes *working shell/state* from *desired synthesis behaviour*.

| Area | Implemented today | Desired / not implemented |
| --- | --- | --- |
| Application | PyQt6 QMainWindow, menus, Layer A/B tab navigation, docked preset browser | approved UI overhaul |
| Section layout | Fixed visible bordered ControlGroup, no scrolling panels, preset list pagination | waveform/analysis region and further Qt style polish |
| Param edits | ParameterControl bindings to StateController, undo/redo, reset | shared slider-plus-spinbox rows, graph-based edits |
| Layer control | Enabled, level, pan, transpose, mute, solo stored for both layers | actual audio effects of those controls |
| Per-layer oscillator | Two oscillators, each waveform, octave, semitone, fine, level | audio oscillators, custom wavetable editor, anti-alias verification |
| Oscillator choices | sine, triangle, saw, square, noise | custom only after model migration; no implemented pulse-width parameter |
| Mixer | osc1_level, osc2_level, mix | operational gain staging; no noise-level row in state |
| Filter | lowpass, highpass, bandpass, notch; cutoff, resonance, key_track, env_amount | real-time filter DSP, actual response graph, drag handles |
| Amp envelope | attack, decay, sustain, release | gate-aware ADSR audio |
| LFO | sine, triangle, saw, square; rate, depth, destination | running modulation audio; editable custom curve is future |
| LFO destinations | filter, pitch, amplitude | correct per-voice routing, smoothing, modulation wheel mapping |
| Master | volume and pan persisted, UI editable | real stereo mix/output |
| Presets | JSON .spyzr v1, default Init Patch, v0 migration, unknown field preservation, atomic save, version guard | real factory presets; serialize future custom waves safely |
| File actions | New/Open/Save/Save As, discard prompt, undo/redo, reset | UI toolbar rearrangement only |
| Browser | folder selection, .spyzr search, explicit Load, paged list | no fabricated bundled preset bank |
| Audio | menu placeholders disabled, status says not connected | pyo backend, devices, engine lifecycle, panic and meters |
| MIDI | menu placeholders disabled, panic is an informational message | note on/off, velocity, bend, mod wheel, sustain, device select |
| Documentation | static HTML/Markdown manual and baseline tests | truthful "planned vs working" flags, design/dev contracts |
| Scenes | no scene model, no scene switching | not in scope; Layer A/B and graph mode are the documented navigation |

## Exact per-layer parameter inventory (32)

**Layer utilities: 6** — enabled (bool), level (0..1), pan (-1..1), transpose (-24..24 integers), mute (bool), solo (bool).

**Oscillator 1: 5; Oscillator 2: 5** — waveform (sine/triangle/saw/square/noise), octave (-3..3 integers), semitone (-12..12 integers), fine (-1..1), level (0..1).

**Mixer: 3** — osc1_level (0..1), osc2_level (0..1), mix (-1..1).

**Filter: 5** — type (lowpass/highpass/bandpass/notch), cutoff (0..1), resonance (0..1), key_track (0..1), env_amount (-1..1).

**Amp envelope: 4** — attack (0..10 seconds), decay (0..10 seconds), sustain (0..1), release (0..10 seconds).

**LFO: 4** — shape (sine/triangle/saw/square), rate (0..20 Hz), depth (-1..1), destination (filter/pitch/amplitude).

**Shared master: 2** — volume (0..1), pan (-1..1).

ParameterSpec path is the contract, including layer-index paths: ("layers", "0" or "1", "filter", "cutoff") etc. Do not rename keys to match cosmetic labels. In particular, the current UI labels "Fine" as cents, but the persisted ±1 value has no established cents-to-frequency mapping; define and test that conversion in the DSP milestone, rather than inventing units visually.

## Existing file behaviour

- New patch starts with two independently editable layers; A is enabled, B is disabled.
- Both layer states and global controls are persisted in version 1 format.
- Loading version 0 migrates to version 1. Unsupported future versions must be rejected, not silently downgraded.
- Unknown fields are preserved by the existing migrate/validate/save implementation. Explicitly regression-test that property whenever adding a new waveform field.
- A real preset browser populates from a chosen directory. It does not have a built-in factory preset catalog today.
- Saved status (dirty marker) is driven by the undo stack. Keep the contract for slider, graph and programmatic edits.

## Documentation inconsistencies to resolve

- The user-facing manual sometimes uses present tense for MIDI selection and audible playback, but both backends are unconnected. Do not claim they are presently operational.
- The feature manual describes modulation and filter-envelope behaviour as the desired sound path, not audio that already exists.
- The approved screenshot is a style brief: some numeric labels and controls do not match ParameterSpec.
- No independent Scene or Song feature exists. Do not infer one from conversations about switching visual sections.

## Product scope boundary

This repo is the **Synthepyzer two-layer desktop subtractive synth**. It is not the separate Rails DAW, DJ deck, sample browser, or sequencer project. Do not introduce unrelated navigation, sampler tracks, FX racks, arbitrary new modulation panels, or existing-fake factory patches merely to mimic a generic software synthesizer.
