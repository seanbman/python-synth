# Codex instructions: Synthepyzer

Before making UI or audio changes, read these files in order:
1. docs/development/CODEX_IMPLEMENTATION.md
2. docs/development/APPROVED_UI.md
3. docs/development/FEATURE_AUDIT.md
4. docs/development/AUDIO_ENGINE.md
5. docs/assets/synthepyzer-approved-ui.png
6. synthepyzer/parameters.py, state.py, binding.py, preset.py, main_window.py, panels.py and controls.py

The approved mockup is **visual direction only**. The code and documented parameter inventory define existing features. Do not implement screenshot hallucinations, fake presets, false audio status or fabricated Hz/dB labels. The name is **Synthepyzer**.

Preserve **PyQt6, a two-layer instrument, native compact sliders with rectangular thumbs, magenta #C2187A, neutral greys, visible bordered non-collapsible groups and no scrollbars**. Preserve StateController, undo/redo, real preset browser, and .spyzr migration/unknown-field preservation. The synthesized audio/MIDI backend is not yet connected. The selected future audio backend is **pyo 1.1.0**, with NumPy for offline analysis only when necessary.

Do **not** invent Scene, Song, Track, Sequencer, Sampler, fake noise-level control or additional effects just because a model-generated UI includes them. Layer A/B are real. Graph-mode navigation is planned. Custom waveform editing requires a distinct state model, migration, tests and real DSP linkage.

Before claiming a change is complete, run:

    QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v

Check actual Qt geometry at the minimum supported window size and real screenshots. Add tests for any new interactive feature; never present a generated concept screenshot as a screenshot of running code.
