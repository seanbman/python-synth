# Features

Synthepyzer is a compact subtractive synthesizer. Its controls follow the path of a note: create a waveform, combine it with another, remove or emphasize frequencies, shape the note over time, and add movement.

The names below are the control vocabulary for the first instrument. They are written in the same language you will see on the synth panel.

![A sound moving from oscillator through harmonics, filtering, and an amplitude envelope](assets/signal-path.png)

## How a sound is built

Every oscillator produces a repeating electrical-like pattern called a waveform. The pattern repeats at the note’s frequency: a faster repeat is a higher pitch, and a slower repeat is a lower pitch.

The shape of that pattern determines which harmonics are present. Harmonics are additional frequency components stacked above the fundamental pitch. A simple sine wave has only the fundamental; sharper-edged shapes contain more upper harmonics and sound brighter or rougher.

Synthepyzer then processes the oscillator signal in this order:

1. Generate the oscillator waveforms.
2. Tune and blend the oscillators.
3. Shape the tone with the filter.
4. Shape the volume over time with the amp envelope.
5. Add motion with the LFO and performance controls.

## Oscillator section

The oscillator is the sound source. Use Oscillator 1 for the main identity of a patch, then bring in Oscillator 2 when you want more weight, width, or harmonic contrast.

### WAVEFORM

Chooses the repeating shape of the oscillator. The four starting choices are shown below.

![Four oscillator waveform shapes: sine, sawtooth, square, and triangle](assets/waveform-families.png)

- **SINE** is a smooth curve with no upper harmonics. It sounds pure, soft, and flute-like.
- **SAW** rises or falls in a straight ramp before snapping back. Its sharp reset adds many harmonics, making it bright, buzzy, and useful for leads, brass-like patches, and subtractive sweeps.
- **SQUARE** jumps between two levels. It emphasizes odd harmonics and has a hollow, woody, or reedy character.
- **TRIANGLE** moves in straight slopes with softer corners than a square wave. It contains fewer upper harmonics than a saw and sounds rounder while remaining more present than a sine.

### OCTAVE

Moves the oscillator in whole-octave steps. One octave doubles or halves the oscillator frequency while keeping the note relationship intact. Use **OCTAVE** to put Oscillator 2 below the main voice for bass weight or above it for a brighter layer.

### SEMITONE

Tunes the oscillator in half-step increments. Small offsets create intervals; an octave is twelve semitones. Set Oscillator 2 to a fifth or octave for a stable musical blend, or use a close interval for a more complex, slightly tense tone.

### FINE

Makes small pitch adjustments around the selected semitone. When two oscillators are nearly—but not exactly—the same pitch, their wave peaks drift in and out of alignment. This creates **beating**, a slow rise and fall in loudness that can make a patch feel wide or alive.

Keep **FINE** near the center for a focused tone. Increase the offset for a wider, more animated sound; extreme offsets become clearly out of tune.

### LEVEL

Sets how much of that oscillator enters the mixer. More level means the oscillator contributes more to the final sound and may make the filter and amplifier work harder. Start with Oscillator 1 as the anchor, then raise Oscillator 2 until you hear the character you want.

## Mixer section

### OSC 1 LEVEL and OSC 2 LEVEL

These two knobs balance the sound sources before they reach the filter. Moving the balance changes the harmonic recipe even when the filter stays still.

For a clear tone, let one oscillator lead and keep the other lower. For a larger tone, bring both near the same level. If the combined sound becomes too loud or harsh, lower both oscillator levels rather than trying to fix it only with the master volume.

### MIX

The **MIX** control is an optional single-knob way to move between the two oscillators. At the left, Oscillator 1 dominates. At the right, Oscillator 2 dominates. In the middle, both contribute.

When you are learning a patch, use **MIX** to hear exactly what each oscillator is contributing. When you want independent control, use the individual **LEVEL** knobs.

## Filter section

The filter changes the balance of frequencies after the oscillators have been combined. It does not change the note’s fundamental pitch; it changes the tone carried by that pitch.

### CUTOFF

Sets the frequency where the filter begins to reduce energy. With the low-pass filter used for the first instrument, turning **CUTOFF** down removes more high-frequency harmonics and makes the sound darker, softer, and more distant. Turning it up reveals more edge and brightness.

On a saw wave, a slow movement of **CUTOFF** can take the sound from muted and rounded to bright and open without changing the note being played.

### RESONANCE

Adds emphasis around the cutoff frequency. A small amount gives the filter a more focused, vocal quality. Higher values create a pronounced peak that can whistle or ring as the cutoff moves.

Resonance does not simply make the whole sound louder. It concentrates energy in a narrow band, so use it with **CUTOFF** to find the part of the sound you want to highlight.

### KEY TRACK

Makes the filter follow the keyboard. Without key tracking, the same cutoff frequency affects every note equally, so high notes may become much darker than low notes. Increasing **KEY TRACK** raises the cutoff for higher notes and lowers it for lower notes, keeping the patch’s brightness more consistent across the keyboard.

### ENV AMOUNT

Lets the amp envelope’s movement push the filter cutoff. Positive **ENV AMOUNT** opens the filter at the beginning of a note and lets it close as the envelope decays. This is the control that turns a static bass tone into a pluck or gives a lead a bright initial bite.

## Amp envelope section

The amplifier envelope controls how the volume changes from key press to key release. It does not change the waveform’s shape directly; it changes the amplitude of the waveform over time.

### ATTACK

Controls how long the sound takes to reach its initial peak after a key press. A short **ATTACK** makes the note speak immediately. A longer **ATTACK** creates a swell that fades into the note.

### DECAY

Controls how long the sound takes to move from its initial peak down toward the sustain level. Short **DECAY** gives a pluck or percussive front edge. Longer **DECAY** lets the opening character remain present.

### SUSTAIN

Sets the level held while the key remains down after the decay stage. **SUSTAIN** is a level, not a time: it determines how loud the held part of the note is.

### RELEASE

Controls how long the sound fades after the key is released. A short **RELEASE** keeps phrases clean and separated. A longer **RELEASE** lets notes trail into one another and is useful for pads and slow melodies.

## Modulation section

The low-frequency oscillator, or LFO, is a slow-moving control signal. It is normally below the range of hearing as a pitch, but its changing value can move another parameter for you.

### LFO SHAPE

Chooses the pattern of the modulation signal. A sine shape moves smoothly; a triangle shape moves at a steady rate; a square shape switches between two values for a rhythmic change.

### LFO RATE

Sets how quickly the modulation cycle repeats. Slow **LFO RATE** creates a gradual sweep or gentle vibrato. Faster rates create tremolo, rapid vibrato, or a more obvious rhythmic pulse.

### LFO DEPTH

Sets how far the LFO moves its destination. At zero, the LFO is running but inaudible because it has no influence. Increase **LFO DEPTH** until the motion is noticeable, then back it down until it supports the note instead of distracting from it.

### LFO DESTINATION

Chooses what the LFO moves:

- **PITCH** creates vibrato by moving the oscillator frequency around the played note.
- **FILTER** creates a repeating brightness sweep.
- **AMP** creates tremolo by moving the volume up and down.

## Output section

### VOLUME

Sets the final level sent to the audio output. Use it to match Synthepyzer to the rest of your setup. If a patch sounds harsh or distorted, lower the oscillator **LEVEL** controls first; use **VOLUME** for overall listening level.

### PAN

Places the instrument between the left and right speakers. Keep **PAN** centered for a focused mono-compatible sound. A small offset can give a layered patch a sense of space, but it should not replace careful oscillator tuning.

## Performance controls

The synth responds to the controls that make a keyboard performance expressive:

- **VELOCITY** carries how hard a key is played and can make a note louder or brighter.
- **PITCH BEND** moves pitch smoothly above or below the played note.
- **MOD WHEEL** controls the expressive modulation amount while you play.
- **SUSTAIN** holds notes after the keys are released.

Read [MIDI Controllers](#/midi-controllers) for the playing workflow, or visit [Playing](#/playing) for practical combinations of these controls.

> The most useful habit is to change one knob at a time. Hold a note, listen for the change in the waveform’s brightness, movement, or amplitude, and then decide whether the patch needs more or less.
