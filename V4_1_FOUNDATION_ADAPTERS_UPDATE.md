# V4.1 Foundation + Adapter Update

This update responds to five problems found in the first full-song report:

```text
P0: Structure should feel more like music structure, not only novelty cuts.
P1: Add MIDI-like simplification.
P2: Add source separation / instrument evidence path.
P3: Add vocal transcription / lyric alignment path.
P4: Rewrite listening notes so they do not sound like dead templates.
P5: Keep MSSL spatial narrative after the foundation layer.
```

## Script update

Updated:

```text
scripts/run_full_song_analysis.py
```

Version now reports:

```text
mssl_full_song_analysis_v4_1_foundation_adapters
```

## New default outputs

Each segment now includes:

```text
musical_structure
midi_like_skeleton
source_instrument_evidence
lyric_alignment
audio_terms_summary
ome_mapping
object_candidates
listening_report_note
```

## P0

Structural boundaries are still lightweight, but they now snap toward the song's bar-like grid when possible. Each segment receives a heuristic role label:

```text
intro_like
verse_like
chorus_like
bridge_like
breakdown_like
outro_like
instrumental_like
section_like
```

## P1

The runtime now emits a MIDI-like skeleton proxy:

```text
melody_contour_proxy
bass_motion_proxy
harmony_block_proxy
phrase_shape
note_density_proxy
```

This is not real transcription. Real transcription should later be optional through Basic Pitch / Omnizart / MT3.

## P2

Default runtime does not separate stems. It now writes a source/instrument evidence object that clearly says `not_separated` and lists only full-mix source hypotheses.

Future optional adapters: python-audio-separator / Demucs.

## P3

Default runtime does not transcribe lyrics. It now writes lyric alignment status with `not_run` and a vocal activity candidate.

Future optional adapters: Qwen3-ASR / FunASR / WhisperX.

## P4

Added:

```text
docs/listening_language_layer_draft.md
```

Segment notes now use a first draft of MSSL's natural listening language layer.

## P5

MSSL spatial fields remain, but they no longer appear before the basic song foundation.

The report order is now:

```text
metadata
song-level pulse / style
music-like structure map
external adapter registry
foundation + MSSL segment table
listening notes
```
