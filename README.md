# Synthepyzer

Synthepyzer is a planned two-layer MIDI software synthesizer. The repository is currently documentation-first, with a dependency-free state and preset foundation ready for the PyQt6 UI and audio engine.

## Documentation

Start the local manual from the repository root:

```text
python3 -m http.server 8000
```

Open [http://localhost:8000/docs/](http://localhost:8000/docs/).

## Preset foundation

The core model supports two stacked layers and versioned, human-readable `.spyzr` presets:

```text
python3 -m unittest discover -s tests -v
```

Presets migrate forward and retain unknown fields so future controls can be added without silently discarding newer data.

## Scroll-free desktop layout

The PyQt6 instrument window uses a fixed-viewport control grid rather than scrollable
sections. Layer utility spans the top; oscillators sit side by side; filter and
envelope share the next row; mixer and LFO share the bottom row; master output
stays beneath the layer tabs. All 32 parameters on the selected layer are
accessible without vertical or horizontal scrolling at the minimum supported
window size (1000 × 680). The preset browser pages through results instead
of displaying scrollbars.

Run the headless UI and state tests after any layout change:

```sh
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

## Optional PyQt6 shell

Install the desktop UI dependency when you are ready to run the application:

```text
python3 -m pip install -e '.[ui]'
python3 -m synthepyzer.app
```
