# Codex execution plan — align Synthepyzer with approved mockup

Priority: **implementation instructions for Codex**, not a description of completed code. Date 2026-11-11.

Required reading (in order):
1. ../assets/synthepyzer-approved-ui.png — **exact approved reference**.
2. APPROVED_UI.md — visual/navigation and graph interactions.
3. FEATURE_AUDIT.md — actual implemented feature and state inventory.
4. AUDIO_ENGINE.md — pyo decision, mappings, lifecycle and DSP responsibilities.
5. ../content/features.md, ../content/layers-and-presets.md and ../content/midi-controllers.md — product behaviours.
6. ../../synthepyzer/{main_window,panels,controls,parameters,state,binding,preset}.py and ../../tests/ — **inspect current code** before modifying.

## Invariants (do not regress)

- Desktop native **PyQt6**, product spelled **Synthepyzer** everywhere. No fake functions from generated image.
- Two fully independent Layers A/B; each with exactly the currently defined 32 parameters, plus two global controls. Keep state paths, real button behaviours, undo/redo and on-disk format until a versioned migration.
- **Never render any scrollbars**, vertical or horizontal, inside the main instrument, dock/browser or graph. No clipped content or inaccessible commands.
- **No collapsible group panels**; keep all groups visibly bordered and fixed. Layer navigation via tabs/buttons and graph mode via clearly labeled selectors; no "Scene" object exists.
- Real Qt horizontal sliders with narrow rectangular grey thumbs, magenta fill, parameter label on left, ONE adjacent numeric input/value on right; remove repeated captions and gratuitous tiny icons.
- Greys and black graphs, custom magenta **#C2187A** accent; **no green or orange**. Styled controls should still respond to disabled/focus/hover states and be keyboard accessible.
- Preserve the right-side file-based preset browser and page navigation. No fabricated factory presets or activity meters.

## Scope: milestone-by-milestone, test after each

**M1 — Static shell rebuilt to match reference.**
- Use the supplied screenshot as a composition guide, but derive control inventory and valid values from ParameterSpec/state.
- Rework main_window.py, panels.py, controls.py into desktop toolbar + explicit Layer A/B navigation + plot region + permanently visible group boxes + lower output strip.
- Keep proper menus and settings. Keep native QSlider/QDoubleSpinBox/QSpinBox/QComboBox/QCheckBox where appropriate. Bidirectional slider/spinbox binding must update StateController once per user change, preserving undo semantics and avoiding recursive emissions. Use one display formatter per parameter.
- Rename only cosmetic labels; do not rename existing state keys.
- For the graph region, render a truthful **inactive placeholder** ("Waveform editor — coming in next milestone") until real interaction exists; do not misrepresent generated curves as connected output.
- Use actual default "Init Patch" and actual .spyzr files, not list from mockup. No screenshot-only Noise Level row.
- No collapsing widgets. Remove old section toggles and unused controls, and ensure both layers switch without resetting edits.
- At 1000x680, if a full graph and 32 controls cannot physically fit legibly, reorganize content into explicit tabbed pages (e.g. Edit | Analyze) or a contained plot-mode stack; never rely on hidden overflow, browser zoom, fake controls or scrolling.

**M2 — Editable waveform and deterministic visualization.**
- Implement QWidget/QPainter graph, target OSC 1/2 selector, nodes and optional tangents, pointer hit testing, position constraints and periodic seam. A graph drag must mutate actual model state, be reversible in one undo action, and update preview.
- Add a custom waveform only with versioned .spyzr data model change. Keep shipped preset waveform options unchanged until that migration.
- Implement filter response readout with LP/HP/BP/notch graph shape, interactive cutoff and resonance handles; link graph <-> normalized sliders <-> state via one conversion rule.
- LFO graph previews supported shapes; custom draggable LFO is explicitly separate future work.
- Plot axes must be accurately labeled. Expose selected Layer/OSC/type without relying on color alone. Include Reset state, loading saved custom waves and invalid-node sanitization.

**M3 — pyo DSP engine.**
- Add optional audio dependency, modular engine interface, lazy pyo.Server lifecycle, normalized-to-physical parameter mapper and two-layer voice graph per AUDIO_ENGINE.md.
- Keep pure-model tests headless. No second audio output library unless warranted and documented. Avoid callbacks touching Qt widgets.
- Provide hardware-independent offline DSP/state tests and a manual Linux listening checklist.
- Do not announce "backend connected" until an actual audio callback outputs sound on selected device.

**M4 — MIDI and performance behaviours.**
- Wire note-on/off/polyphonic voice release, velocity, pitch bend, mod wheel, sustain, MIDI selection, panic. Ensure octave/semitone/fine/transpose mappings, routing and solo/mute audible.
- MIDI status and device menus must reflect actual devices and errors, not stub statuses.

**M5 — Preset reliability and finish.**
- Integrate custom-wave serialization/migration, preset load/save/dirty indicator and undo/redo. Do not discard unknown fields.
- Add actual factory presets only after sound and preset content have been authored and tested.
- Polish contrast, compact layouts and keyboard accessibility to match screenshot while remaining functional.

## Required tests and proof

Execute (install UI extra first):
    QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v

Add tests for:
- Full parameter inventory and binding to active layer, including no cross-layer changes.
- No QScrollArea or any visible/usable horizontal/vertical scrollbar at 1000×680, 1180×760 and 1536×1024; including preset paging. Exact usable viewport must contain every currently displayed widget.
- Permanent ControlGroup/QGroupBox visibility, no checkable collapsible headers or Expand/Collapse menu items.
- Real slider/spinbox equality, state sync, reset, undo/redo, preset replacement, save/reload.
- Graph mouse press/drag/release, graph hit testing, bounds, seam, one undo step per drag, row-to-plot parameter round trip.
- Filter plot correctness for each filter type, amplitude normalization and sample rates.
- MIDI note on/off/polyphony/panic and audio lifecycle via fake backend; never require audio hardware for CI.
- At least one manual screenshot and visual review of real Qt UI, not synthesized image, with 100%, 125% and 150% scaling if available.

No claims of completion without passing tests. If a test fails, fix the implementation/test contract rather than deleting the test. Record commands used, output, a short before/after visual summary, and the exact Git commit/branch in your handoff.

## Explicit prohibitions

Do not import a web UI framework, replace PyQt6, add Node/Docker/SuperCollider, invent a scene/song/track page, create fake preset names, fake CPU/audio telemetry, arbitrary noise channel, PWM control, effect rack, or LFO sync toggle. Do not change stored parameter units just to reproduce the screenshot. Do not silently remove existing controls, presets, or field migration. Do not force entire application code into one file or perform a sweeping rewrite unrelated to the current milestone.

## Work discipline

Use small cohesive commits, run tests after every milestone, preserve working files and user changes, update documentation when actual shipped capability changes, and record unresolved differences between mockup and code rather than treating generated pixels as a specification of executable behaviour.
