# Layers & Presets

Synthepyzer can make a sound from one layer, or combine two complete synth layers into one playable patch. This gives you the weight of a stacked instrument without hiding the individual sounds that make it up.

## Switching layers versus scenes

The implemented navigation is **Layer A / Layer B** at the top of the instrument. There is **no Scene model or scene switcher**. Each layer has its own settings, and clicking a layer tab changes which one you edit without enabling or disabling it.

The approved future visualizer will have separate **Waveform / Filter Response / LFO Shape** viewing modes; changing the graph mode will not change the patch or the active layer. Preset loading remains a separate, explicit file action.

## Layer A and Layer B

Each layer has its own oscillator, mixer, filter, amp envelope, and LFO controls. Both layers listen to the selected MIDI input and respond to the same notes by default.

Use the layer tabs to move between **LAYER A** and **LAYER B**. Start with Layer A as the main sound, then enable Layer B when you want another octave, waveform, envelope, or filter shape underneath it.

## Layer controls

The layer strip gives each side of a patch a few controls that do not belong to the oscillator or filter:

- **ENABLE** turns the layer on or off without deleting its settings.
- **LEVEL** sets how much of the layer enters the shared master output.
- **PAN** moves the layer left or right in the stereo field.
- **TRANSPOSE** shifts the entire layer in semitones while the MIDI keyboard continues to play normally.
- **MUTE** silences the layer temporarily.
- **SOLO** lets you listen to the layer by itself while you adjust it.

Layer-level controls happen after that layer’s oscillator, filter, envelope, and LFO processing. The shared master controls happen after both layers have been combined.

## Layering ideas

### Weight and definition

Use a low saw layer for weight and a quieter triangle or square layer for definition. Keep both layers near the same pitch, then use **FINE** on one oscillator to introduce a slow beating pattern.

### Bright attack, soft body

Give Layer A a short, bright envelope and use Layer B with a slower attack and lower filter cutoff. The first layer provides the note’s edge; the second makes the held note feel full.

### Octave foundation

Keep Layer A at the played pitch and set Layer B’s **TRANSPOSE** to one octave below. Lower Layer B’s **LEVEL** until the patch gains weight without becoming muddy.

## Master output

The shared master strip contains the final **VOLUME** and **PAN** controls. Master volume changes the level of the combined patch; it does not change the balance between layers. Adjust the layer levels when you want to change the sound’s recipe, and use master volume to match Synthepyzer to the rest of your setup.

## Saving a preset

Choose **Save** or **Save As** to store the complete patch in a `.spyzr` file. A preset includes:

- The name, author, tags, and timestamps.
- Master output settings.
- The enabled state and layer controls for Layer A and Layer B.
- Every oscillator, mixer, filter, envelope, and LFO setting in each layer.

The file is human-readable JSON, but you do not need to edit it by hand. Keep the extension intact so Synthepyzer can recognize it when you open it later.

## Loading a preset

Choose **Open** and select a `.spyzr` file. Loading replaces the current patch only after the file has been read and checked. If the file is damaged, incomplete, or from an unsupported future format, Synthepyzer leaves the current sound in place and explains the problem.

## Built for future features

Every `.spyzr` file includes a format version. When the format gains new controls, Synthepyzer can migrate older files forward. Fields from newer versions that the current app does not understand are retained when possible, so saving a preset does not silently erase future settings.

> A preset is the complete instrument state, not only the visible knob positions. Layer balance, mute state, tuning, metadata, and future-compatible fields travel with the sound.
