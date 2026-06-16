# MSSL V4.1 Adapter Design

V4.1 fixes the order of the full-song report:

```text
foundation first
-> MSSL spatial interpretation second
-> final listening narrative last
```

## Default runtime

The default script remains lightweight and requires only `numpy`.

It now emits:

```text
P0 music-like structure map
P1 MIDI-like skeleton proxy
P2 source / instrument evidence status
P3 lyric alignment status
P4 listening language draft
P5 MSSL spatial interpretation
```

## Optional adapter principle

External tools must not become the conceptual core.

```text
external tool output = evidence
MSSL = translation + relation + report
```

## P0 structure adapter

Input:

```text
full WAV / frame features / optional external structure labels
```

Output:

```json
{
  "role_label": "intro_like | verse_like | chorus_like | bridge_like | outro_like | section_like",
  "section_function": "...",
  "bar_index_range": "...",
  "boundary_basis": "..."
}
```

Default implementation:

```text
novelty peaks + bar-grid snapping + heuristic role labeling
```

Future optional adapters:

```text
MSAF / librosa / LinkSeg / All-In-One Music Structure Analyzer / madmom
```

## P1 MIDI-like skeleton adapter

Input:

```text
segment audio evidence + optional MIDI transcription
```

Output:

```json
{
  "melody_contour_proxy": "rising_contour | falling_contour | stable_or_reciting_contour | blurred_contour",
  "bass_motion_proxy": "repeated_low_anchor | low_anchor_stable | bass_drops_or_thickens | bass_rises_or_opens | bass_light_or_absent",
  "harmony_block_proxy": "dark_stable_harmonic_block | dark_compressed_low_block | wide_sustained_harmonic_field | brighter_release_or_upper_residue",
  "phrase_shape": "long_sustained_phrase | dense_pulsed_phrase | compressed_center_phrase | release_tail_phrase",
  "note_density_proxy": "sparse | medium_sparse | medium | dense"
}
```

Default implementation:

```text
full-mix symbolic proxy only
```

Future optional adapters:

```text
Basic Pitch / Omnizart / MT3
```

## P2 source separation adapter

Input:

```text
full mix + optional separated stems
```

Output:

```json
{
  "status": "not_separated | separated",
  "full_mix_source_hypotheses": [],
  "stem_support": {}
}
```

Default implementation:

```text
full-mix source hypotheses only
```

Future optional adapters:

```text
python-audio-separator / Demucs
```

Boundary:

```text
instrument evidence is not object identity
```

## P3 vocal transcription adapter

Input:

```text
vocals stem or full mix + optional ASR / forced alignment
```

Output:

```json
{
  "status": "not_run | transcribed | aligned",
  "vocal_activity_candidate": 0.0,
  "lyric_phrase": null,
  "timestamp_granularity": null
}
```

Future optional adapters:

```text
Qwen3-ASR / FunASR / WhisperX
```

Boundary:

```text
no singer identity
no voiceprint
no long public lyric dump
```

## P4 listening language layer

See `docs/listening_language_layer_draft.md`.

## P5 MSSL spatial narrative

Only after P0-P4 are present does the report translate into:

```text
O-space source candidates
M-domain mapping rules
E-space receiver-side listening coordinates
object relation graph
human-readable listening note
```
