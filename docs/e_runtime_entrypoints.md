# E. Runtime and Entrypoints

Status: consolidated current runtime / script entrypoint guide.

Use this file to keep README and script help text aligned with the actual main path.

Consolidated from:

- `runtime_pipeline.md`
- `scripts_inventory.md`
- `full_song_analysis_pipeline.md`
- `detailed_runtime_flow.md`
- `portable_path_audit.md`
- `ome_spatial_filter_bank_design.md`
- `ome_spatial_filter_bank_handoff_contract.md`
- `ome_spatial_filter_bank_reading_notes.md`

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
-> song identity layer
-> reconstructed stream / score layer
-> symbolic timeline MIDI layer
-> optional external recognition command / adapter packet
-> external strong recognition layer
-> OME Spatial Filter Bank runtime layer
-> temporal-timbre object candidate layer
-> musical object performance layer
-> lyric context layer
-> professional audio terminology report
-> compact online AI handoff + full trace
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

Continuation pipeline. It connects full-song structural analysis, song identity, reconstructed stream / score generation, symbolic timeline MIDI generation, optional external recognition commands, external family evidence normalization, OME runtime mapping, temporal-timbre object candidates, musical object performance cards, lyric context, professional terminology handoff generation, family gate insertion, and optional context injection.

```text
scripts/run_full_song_analysis.py
```

Structural front half. Produces the full-song profile used by the downstream identity, MIDI, object, performance, terminology, lyric-context, and handoff builders.

```text
scripts/build_song_identity_layer.py
```

Builds bounded song identity status from supplied metadata, identity JSON, and filename/analysis hints. It does not infer title or artist from raw audio features by itself.

```text
scripts/build_reconstructed_stream_score_layers.py
```

Aggregates segment-level full-mix evidence into functional reconstructed streams and a compact score skeleton. This is not original stem recovery and not true MIDI transcription.

```text
scripts/build_symbolic_timeline_midi_layer.py
```

Builds the music-time skeleton: beat/bar context, section timeline, and symbolic event streams for voice-like, bass-like, rhythm-like, harmonic-like, and texture/FX-like activity. Default output is full-mix symbolic timeline evidence, not original MIDI truth. Optional adapter packets can attach Basic Pitch / MT3 / Omnizart / user transcription evidence as bounded real-MIDI support.

```text
scripts/build_external_strong_recognition_layer.py
```

Normalizes external family evidence from command-generated or pre-existing adapter JSON packets. This layer decides which vocal, instrument, and effect-family names may be used downstream. It does not prove source truth, performer identity, exact original stems, lyric truth, or creator intent.

```text
scripts/adapters/normalize_external_recognition_packet.py
```

Normalizes generic external tool JSON into the MSSL external recognition adapter packet shape.

```text
scripts/attach_family_gate.py
```

Post-pass that inserts the family gate into the evidence pack, critical brief, compact handoff, and full trace handoff. This is called by the main experience pipeline.

```text
scripts/build_ome_spatial_filter_bank_layer.py
```

Builds a receiver-side OME spatial field / spatial-band support layer. This maps supported material into spatial evidence; it must not be read as the sole object generator.

```text
scripts/build_temporal_timbre_object_candidate_layer.py
```

Builds auditory object-family candidates from time-frequency-timbre continuity, source-family hints, optional external adapter evidence, symbolic timeline support, and optional OME mapping support. Object candidates come before musical performance language.

```text
scripts/build_musical_object_performance_layer.py
```

Builds vocal / instrumental / effect-family performance cards. This layer is intentionally not a machine behavior layer. Specific family cards require the external family gate; otherwise the layer collapses to functional object language.

```text
scripts/build_lyric_context_layer.py
```

Builds bounded lyric context from optional local lyric/alignment files plus MSSL vocal, MIDI, and OME anchors. It does not export full lyrics into report-facing handoff.

```text
scripts/build_listening_experience_prompt.py
```

Builds the professional evidence pack, critical brief, technical prompt input, and online handoff.

```text
scripts/build_listening_experience_prompt_with_descriptors.py
```

Descriptor-aware wrapper. It attaches song identity, lyric context, subjective descriptor validation, OME packet material, symbolic timeline MIDI layer, external recognition status, musical object performance layer, compact handoff, and full trace handoff.

```text
scripts/render_compact_online_handoff.py
```

Renders the compact online handoff as a report-composer schema: song identity, source-family permission, vocal/lyric anchors, instrument/source-family performance, MIDI/melody/rhythm skeleton, general audio evidence, OME spatial performance state, macro arc, and writing boundaries.

```text
scripts/build_aesthetic_context_handoff.py
```

Injects optional local context into the handoff Markdown. Context is not treated as local truth.

## Song identity contract

Song identity can be supplied through:

```text
--song-title
--song-artist
--song-album
--song-year
--song-identity-json
```

Boundary:

```text
MSSL audio evidence alone does not prove title or artist.
Song identity requires supplied metadata, external identity evidence, fingerprint/search context, or online verification.
```

## Lyric context contract

Lyric context can be supplied through:

```text
--lyrics-file path/to/lyrics.txt
--lyric-alignment path/to/alignment.json
```

MSSL does not copy full lyrics into the report-facing handoff. It records source/alignment status and connects verified lyric context to vocal timing, MIDI phrase behavior, and OME spatial anchors.

Boundary:

```text
lyric file != lyric truth unless externally verified
lyric alignment != exact performance truth unless adapter quality is known
MSSL vocal anchors != singer identity
```

## MIDI layer contract

MIDI in MSSL means a music-time skeleton. It must not be reduced to a decorative prompt phrase, and it must not be falsely promoted into original score truth.

Default layer:

```text
full-mix beat / bar grid
+ structural segment timeline
+ symbolic event streams
+ phrase / density / contour / bass / harmony proxies
```

Optional real-MIDI adapter:

```text
--midi-adapter path/to/adapter_packet.json
```

Expected adapter role:

```text
Basic Pitch / MT3 / Omnizart / user MIDI packet
-> bounded transcription evidence
-> refined timing, contour, density, track-family support
```

Boundary:

```text
adapter-backed MIDI evidence != original MIDI truth
adapter track family != confirmed source identity
```

## External family evidence contract

MSSL must support the target report goal:

```text
song type / listening context
+ vocal, instrument, and effect-family performance
+ MIDI / melody behavior
+ OME spatial state
-> online-AI close-listening handoff
```

There are three accepted paths.

Pre-existing packet:

```text
--external-recognition path/to/recognition_packet.json
```

Main-flow command:

```text
--external-recognition-command "python recognizer.py --input {input} --output-json {output_json}"
```

Generic normalization:

```text
python scripts/adapters/normalize_external_recognition_packet.py --input-json raw_tool_output.json --output-json recognition_packet.json
```

Placeholders:

```text
{input}       decoded or original audio path when available
{profile}     full-song profile path
{output_dir}  current song output directory
{output_json} required JSON path that the command must write
```

The command-generated JSON is immediately fed into `build_external_strong_recognition_layer.py`, then used by `build_musical_object_performance_layer.py` and `attach_family_gate.py`.

## OME runtime contract

The OME runtime layer is the receiver-side spatial field / mapping support layer. It is not a source extractor and not the object identity generator.

Input evidence belongs to stereo and time-frequency analysis:

```text
channel level difference
channel phase / time relation
mid-side energy
interchannel correlation
frequency-band behavior
primary / ambient evidence
direct / reflected / diffuse response cues
transient vs sustained behavior
```

Output should be read as:

```text
receiver-side spatial-band support
-> professional terminology anchor
-> subjective attribute mapping
-> online-AI review affordance
```

Do not let OME stream names directly become review prose.

## Runtime reading

Do not read the current path as:

```text
audio -> features -> normal review
```

Read it as:

```text
recorded signal evidence
-> structural segments
-> song identity status
-> audio mechanism evidence
-> reconstructed stream / score skeleton
-> symbolic timeline MIDI layer
-> external family evidence gate
-> OME receiver-side field mapping
-> temporal-timbre object candidates
-> musical object performance cards
-> lyric context anchors
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
+ symbolic timeline support
+ bounded source-family hints
+ optional external adapter evidence
-> object-family candidate
-> musical object performance card
-> OME receiver-side mapping
```

## Full-song segment unit

The main evidence unit is no longer a one-second block.

```text
structural segment = main evidence unit
frame evidence = internal support layer
beat / bar grid = rhythm reference layer
symbolic MIDI events = music-time support layer
external recognition events = optional family evidence layer
lyric alignment anchors = optional semantic timing layer
```

One-second frames may still exist for inspection, but they should not become the main listening unit.

## Output folder policy

Default output shape:

```text
outputs/<song-folder>/
  <input-stem>_full_song_profile.json
  listening_experience_evidence_pack.json
  critical_listening_brief.json
  song_identity_layer.json / .md
  reconstructed_stream_score_layer.md
  symbolic_timeline_midi_layer.json / .md
  external_strong_recognition_layer.json / .md
  ome_spatial_filter_bank_layer.json / .md
  temporal_timbre_object_candidate_layer.json / .md
  musical_object_performance_layer.json / .md
  lyric_context_layer.json / .md
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

With identity and lyric context:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --song-title "Song title" --song-artist "Artist" --lyrics-file "path\to\lyrics.txt" --lyric-alignment "path\to\lyric_alignment.json"
```

With optional MIDI adapter:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --midi-adapter "path\to\midi_adapter_packet.json"
```

With external recognition command:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --external-recognition-command "python path\to\recognizer.py --input {input} --output-json {output_json}"
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
