# Changelog

This file consolidates the former root-level V3/V4 update notes. It keeps the useful project history without leaving staged update files in the repository root.

## V4.2 Theory foundation

- Added a theory-support layer without changing runtime code.
- Clarified that MSSL does not invent audio filters, cochlear models, wavelet theory, or DSP; it selects existing mechanisms and translates them into O/M/E evidence.
- Separated support types into direct audio mechanism support, human auditory constraint support, structural analogy, and project-internal definitions.
- Preserved the boundary against overclaiming, such as treating CWT coefficients, RMS changes, stereo width, or comment word frequency as direct listening proof.

## V4.1 Foundation and adapter boundary

- Reordered the full-song interpretation path so foundation evidence appears before MSSL spatial narrative.
- Recorded the intended order as P0 music-like structure, P1 MIDI-like symbolic reduction, P2 source/instrument evidence status, P3 vocal transcription status, P4 listening-language draft, and P5 MSSL spatial interpretation.
- Kept the default runtime lightweight and separated optional adapters from the default path.
- Marked source separation, transcription, and MIDI-like tools as optional evidence providers, not core runtime requirements.

## V4 Full-song structural runtime

- Expanded from short validation clips to local full-song WAV analysis.
- Moved from fixed one-second report units toward audio-derived structural segments.
- Preserved common audio evidence, segment-level O/M/E-style mapping, and auditory object candidates.
- Kept boundaries against source separation truth, singer identity, ASR, lyric recognition, physical 3D localization, and authoritative genre classification.

## V3 Audio object runcheck

- Added a bridge from audio evidence into visualized listening-field object candidates.
- Tracked candidate objects such as rhythmic pulse, floating harmonic/piano-like layer, and vocal-contour-like structure as listening objects, not as confirmed source identities.
- Preserved the rule that audio terms are evidence layers attached after the visualized listening-field representation.

## V3 Object tracking

- Shifted from treating a clip as only a field of proxies to treating it as candidate temporal-spatial auditory objects.
- Established the project chain:

```text
visualized listening field
-> perceptual interval
-> object slot
-> object track
-> listening scene graph
```

- Kept human-guided labels explicitly bounded: not source separation, not automatic instrument recognition, and not automatic voice recognition.

## Repository hygiene

- Root-level staged update notes were merged here.
- Optional external adapter notes now live in `docs/optional_adapters.md`.
- Optional dependency files now live in `requirements-optional/`.
- Generated `outputs/` remain local artifacts and are not part of repository history.
