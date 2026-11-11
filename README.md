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

## Optional PyQt6 shell

Install the desktop UI dependency when you are ready to run the application:

```text
python3 -m pip install -e '.[ui]'
python3 -m synthepyzer.app
```
