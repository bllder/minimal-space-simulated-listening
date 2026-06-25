# E. Runtime and Entrypoints

Status: consolidated current runtime / script entrypoint guide.

Use this file to keep README and script help text aligned with the actual main path.

Consolidated from:

- `runtime_pipeline.md`
- `scripts_inventory.md`
- `full_song_analysis_pipeline.md`
- `detailed_runtime_flow.md`
- `portable_path_audit.md`

## Current human entrypoint

Use this first:

```text
scripts/run_mssl.py
```

Default mode:

```text
experience
```

Current user-facing path:

```text
audio file
-> full-song structural profile
-> reconstructed stream / score layer
-> OME Spatial Filter Bank runtime layer
-> temporal-timbre object candidate layer
-> professional audio terminology report
-> online AI handoff Markdown
```

The main local artifact is:

```text
online_ai_listening_handoff.md
```

Copy or upload that file to an online AI account instead of uploading audio.

## Supported input behavior

The core analyzer reads PCM WAV directly.

The main runner and experience pipeline may decode other common local audio formats through ffmpeg when available:

```text
non-WAV audio
-> temporary PCM WAV
-> run_full_song_analysis.py
```

The temporary decoded WAV is deleted by default unless `--keep-decoded-wav` is supplied.

## Current active scripts

```text
scripts/run_mssl.py
```

Single human entrypoint. Normal users should start here.

```text
scripts/run_listening_experience_pipeline.py
```

Continuation pipeline. It connects full-song structural analysis, reconstructed stream / score generation, OME runtime mapping, temporal-timbre object candidates, professional terminology handoff generation, and optional context injection.

```text
scripts/run_full_song_analysis.py
```

Structural front half. Produces the full-song profile used by the downstream object, terminology, and handoff builders.

```text
scripts/build_reconstructed_stream_score_layers.py
```

Aggregates segment-level full-mix evidence into functional reconstructed streams and a MIDI-like score skeleton. This is not original stem recovery and not true MIDI transcription.

```text
scripts/build_ome_spatial_filter_bank_layer.py
```

Builds a receiver-side OME spatial field / spatial-band support layer. This maps supported material into spatial evidence; it must not be read as the sole object generator.

```text
scripts/build_temporal_timbre_object_candidate_layer.py
```

Builds auditory object-family candidates from time-frequency-timbre continuity, source-family hints, optional external adapter evidence, and optional OME mapping support. Object candidates come before behavior summaries.

```text
scripts/build_listening_experience_prompt.py
```

Builds the professional evidence pack, critical brief, technical prompt input, and online handoff.

```text
scripts/build_aesthetic_context_handoff.py
```

Injects optional local context into the handoff Markdown. Context is not treated as local truth.

## Runtime reading

Do not read the current path as:

```text
audio -> features -> normal review
```

Read it as:

```text
recorded signal evidence
-> structural segments
-> audio mechanism evidence
-> reconstructed stream / score skeleton
-> OME receiver-side field mapping
-> temporal-timbre object candidates
-> professional terminology report
-> online handoff
```

Important boundary:

```text
spatial bin -> object identity
```

is forbidden.

Use:

```text
time-frequency-timbre evidence
+ bounded source-family hints
+ optional external adapter evidence
-> object-family candidate
-> later behavior summary
-> OME receiver-side mapping
```

## Full-song segment unit

The main evidence unit is no longer a one-second block.

```text
structural segment = main evidence unit
frame evidence = internal support layer
beat / bar grid = rhythm reference layer
```

One-second frames may still exist for inspection, but they should not become the main listening unit.

## Output folder policy

Default output shape:

```text
outputs/<song-folder>/
  <input-stem>_full_song_profile.json
  listening_experience_evidence_pack.json
  critical_listening_brief.json
  reconstructed_stream_score_layer.md
  ome_spatial_filter_bank_layer.json / .md
  temporal_timbre_object_candidate_layer.json / .md
  original_song_listening_prompt_input.md
  online_ai_listening_handoff.md
  online_ai_listening_handoff_full_trace.md
```

Generated output files are local artifacts and should not be committed unless explicitly curated.

## Path portability rule

Do not require a specific drive letter or local machine folder.

Allowed in committed instructions:

```text
<project-root>
path/to/local_audio.wav
path\to\local_audio.wav
outputs/<input-stem>/...
```

Avoid machine-specific absolute paths in docs unless they are clearly marked as examples from a local run.

## Main command examples

Windows:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.mp3"
```

With explicit ffmpeg path:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.flac" --ffmpeg-bin "path\to\ffmpeg.exe"
```

Existing profile:

```powershell
python .\scripts\run_mssl.py experience --profile "outputs\song\song_full_song_profile.json"
```

Structural profile only:

```powershell
python .\scripts\run_mssl.py structural --input "path\to\local_audio.wav"
```

## Cleanup rule

Do not add new top-level runner scripts unless they are wired through `scripts/run_mssl.py` or replace an existing entrypoint.
