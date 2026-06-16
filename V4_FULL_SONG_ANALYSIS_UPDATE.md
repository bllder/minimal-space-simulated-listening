# Full Song Analysis Runtime Update

This update expands MSSL from short validation clips into a local full-song runtime.

## Added script

`scripts/run_full_song_analysis.py`

The script reads a PCM WAV file and generates:

- `outputs/<song>_full_song_profile.json`
- `outputs/<song>_full_song_report.md`

## Target

The target input is a local 3-30 minute WAV song.

Shorter clips are allowed for runcheck/testing.

## Main change

The main report unit is no longer one second.

The script now runs:

```text
full WAV
-> frame-level evidence
-> estimated BPM / beat grid
-> audio-derived structural segments
-> segment O/M/E mapping
-> segment auditory object candidates
-> Markdown listening report
```

## What it retains

The report keeps common song-level information:

```text
sample rate
channels
duration
estimated BPM
beat count
bar-like count
style profile candidates
segment table
```

Each segment keeps common audio terms:

```text
RMS / dBFS
peak
spectral centroid
low / mid / high ratio
stereo width proxy
phase correlation
onset density
harmonic / percussive proxy
```

Then it translates those into MSSL spatial dynamics:

```text
left_right
near_far
high_low
perceived_pressure
perceived_width
perceived_spread
perceived_motion
envelopment
```

## Boundary

This update does not implement:

```text
source separation
piano recognition
singer identity
voiceprint recognition
ASR
lyric recognition
true 3D localization
authoritative genre classification
```

The style output is a heuristic style profile, not a final genre classifier.

The spatial output is receiver-side perceived-space proxy, not physical room reconstruction.

## Local command

```powershell
.\.venv\Scripts\python.exe .\scripts\run_full_song_analysis.py --input "D:\CloudMusic\01.WAV" --output-dir outputs
```

Optional:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_full_song_analysis.py --input "D:\CloudMusic\01.WAV" --output-dir outputs --min-segment-seconds 8 --max-segment-seconds 45
```

## Related docs

- `docs/runtime_pipeline.md`
- `docs/full_song_analysis_pipeline.md`
- `docs/audio_processing_mechanism_index.md`
- `docs/mechanism_to_ome_translation.md`

---

# V4.1 Foundation and Adapter Revision

The first full-song runtime proved the pipeline works, but it over-emphasized spatial description before completing the basic song foundation.

V4.1 fixes the order:

```text
P0 music-like structure segmentation
P1 MIDI-like symbolic reduction
P2 source / instrument evidence status
P3 vocal transcription / lyric alignment status
P4 listening language draft
P5 MSSL spatial interpretation
```

The default runtime still requires only `numpy`.

Optional external adapters are documented but not bundled by default:

```text
requirements-mir.txt
requirements-midi.txt
requirements-separation.txt
requirements-transcription.txt
```

New docs:

```text
docs/external_tools_registry.md
docs/adapter_design_v4_1.md
docs/listening_language_layer_draft.md
V4_1_FOUNDATION_ADAPTERS_UPDATE.md
```
