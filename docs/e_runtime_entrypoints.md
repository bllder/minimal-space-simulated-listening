# E. Runtime and Entrypoints

Status: consolidated current runtime / script entrypoint guide.

Use this file to keep README and script help text aligned with the actual main path.

## Current human entrypoint

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
-> song identity command / song identity layer
-> reconstructed stream / score layer
-> MIDI adapter command / symbolic timeline MIDI layer
-> external recognition command / external strong recognition layer
-> OME Spatial Filter Bank runtime layer
-> temporal-timbre object candidate layer
-> optional instrument / source-family object layer
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

## MVP object visibility rule

The current MVP target is to make rough instrument / source-family object candidates visible for the online AI handoff.

Local OME, gammatone / ERB-like, time-frequency, timbre, envelope, transient, harmonic, noise, spatial, MIDI/pitch, and acoustic-prior evidence may support explicit candidate names such as:

```text
voice / vocal-like foreground object
bass / low-register object
drum / percussion object
guitar / plucked object
keyboard / piano object
synth / pad / harmonic object
FX / texture / tail object
```

External recognition and family gate evidence upgrade or verify these candidates. They are not the only permission for the candidate name to appear. Without external support, keep status such as possible, likely-local, weak-local, confused-with, and missing-evidence instead of erasing the object into only functional language.

## Supported input behavior

The core analyzer reads PCM WAV directly. The main runner and experience pipeline may decode other common local audio formats through ffmpeg when available:

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

Continuation pipeline. It connects full-song structural analysis, song identity commands, reconstructed stream / score generation, MIDI adapter commands, symbolic timeline MIDI generation, external recognition commands, external family evidence normalization, OME runtime mapping, temporal-timbre object candidates, musical object performance cards, lyric context, professional terminology handoff generation, family gate insertion, and optional context injection.

```text
scripts/run_full_song_analysis.py
```

Structural front half. Produces the full-song profile used by downstream identity, MIDI, object, performance, terminology, lyric-context, and handoff builders.

```text
scripts/build_song_identity_layer.py
```

Builds bounded song identity status from supplied metadata, identity JSON, and filename/analysis hints. It does not infer title or artist from raw audio features by itself.

```text
scripts/adapters/run_song_identity_adapter.py
```

Normalizes user fields, ffprobe-style metadata JSON, fpcalc / Chromaprint output, or externally produced AcoustID / MusicBrainz lookup JSON into a song identity JSON for `--song-identity-json` or `--song-identity-command`.

```text
scripts/build_reconstructed_stream_score_layers.py
```

Aggregates segment-level full-mix evidence into functional reconstructed streams and a compact score skeleton. This is not original stem recovery and not true MIDI transcription.

```text
scripts/build_symbolic_timeline_midi_layer.py
```

Builds the music-time skeleton: beat/bar context, section timeline, and symbolic event streams for voice-like, bass-like, rhythm-like, harmonic-like, and texture/FX-like activity. Default output is full-mix symbolic timeline evidence, not original MIDI truth.

```text
scripts/adapters/run_basic_pitch_adapter.py
```

Normalizes Basic Pitch / MT3 / custom transcription notes JSON or CSV into the MSSL MIDI adapter packet shape. It may also run an external tool command before normalization. It supplies timing, pitch contour, note density, and track-family hints; it does not prove original MIDI or source identity.

```text
scripts/build_external_strong_recognition_layer.py
```

Normalizes external family evidence from command-generated or pre-existing adapter JSON packets. This layer decides which vocal, instrument, and effect-family names may be treated as externally supported or verified downstream. It does not cancel local source-family object candidates. It also accepts mixed accompaniment / `other` stem evidence as broad backing-bed context, not as a specific instrument claim.

```text
scripts/adapters/run_demucs_adapter.py
```

Normalizes Demucs / UVR stem outputs into external recognition evidence for vocals, bass, drums, and mixed accompaniment. Stem evidence is bounded and may contain bleed, artifacts, or category errors.

```text
scripts/adapters/normalize_external_recognition_packet.py
```

Normalizes generic external tool JSON into the MSSL external recognition adapter packet shape.

```text
scripts/attach_family_gate.py
```

Post-pass that inserts the family gate into the evidence pack, critical brief, compact handoff, and full trace handoff. It avoids duplicating the family gate when the compact handoff already contains the source-family permission table.

```text
scripts/build_ome_spatial_filter_bank_layer.py
```

Builds a receiver-side OME spatial field / spatial-band support layer. This maps supported material into spatial evidence; it must not be read as the sole object generator.

```text
scripts/build_ome_gammatone_envelope_layer.py
```

Standalone auditory front-end bridge. It reads audio plus a full-song profile and writes an ERB/gammatone-like Mid/Side envelope layer. The JSON keeps compact analysis-matrix summaries and rolling 1-5 second support windows; the PNGs use a smoothed/downsampled display matrix for readability. It supports arrangement contrast and later bounded source-family object hypotheses, but it does not confirm instruments, separate sources, use trained models, or simulate biological cochlea truth.

```text
scripts/build_ome_arrangement_contrast_layer.py
```

Builds a second-pass OME arrangement contrast layer from an existing full-song profile. It turns continuous receiver-side spatial, frequency-band, pressure, width, motion, and onset evidence into arrangement lanes, mixed-state zones, and contrast events. When `--gammatone-envelope` contains rolling-window support, those 1-5 second windows drive local contrast, entry, exit, and recurrence events; full profile segments remain macro fallback/support. It also writes optional standalone human-readable views: `ome_arrangement_timeline.png` and `ome_arrangement_readable_summary.md`. These are visual/summary views of receiver-side arrangement evidence, not extra recognition layers. It does not identify instruments or produce source-family certainty.

```text
references/instrument_acoustic_prior_seed.json
```

Second-run-block preparation artifact. This is a hand-coded acoustic prior and filter-template seed for later ranked hypotheses. It is not connected to the default `run_mssl.py` chain and does not identify instruments by itself.

```text
scripts/validate_instrument_acoustic_prior_index.py
```

Validates the instrument acoustic prior seed: required families, MIDI-to-Hz register ranges, filter-template weights, OME lane names, and boundary text. It is a standalone static validator, not a runtime recognition stage.

```text
scripts/build_instrument_prior_filterbank_layer.py
```

Standalone second-run-block Step 2 artifact. It consumes OME/gammatone arrangement windows, the instrument acoustic prior index, and optional symbolic MIDI / pitch evidence to produce ranked acoustic hypotheses per 1-5 second window. It is not connected to the default `run_mssl.py` chain yet and does not provide source-family certainty.

```text
scripts/validate_instrument_prior_filterbank_layer.py
```

No-audio synthetic validator for the prior filterbank layer. It checks local window scoring, broad family hypotheses, no-pitch confidence caps, unresolved pitch gates, OME lane names, Markdown output, and boundary strings.

```text
scripts/build_temporal_timbre_object_candidate_layer.py
```

Builds auditory object-family candidates from time-frequency-timbre continuity, source-family hints, optional external adapter evidence, symbolic timeline support, optional OME mapping support, and optional bounded instrument-prior filterbank support. Object candidates come before musical performance language.

Optional standalone input:

```text
--instrument-prior-filterbank path/to/instrument_prior_filterbank_layer.json
```

This consumes ranked acoustic hypotheses as candidate support only. It is not connected to the default `run_mssl.py` chain yet and does not replace external recognition or family-gate logic.

When this optional bridge is used without pitch/register evidence or external adapter support, instrument-like and effect-like candidates are capped conservatively and the Markdown includes a prior-bridge diagnostic. Functional object candidates may remain strong when full-mix continuity supports them.

```text
scripts/build_instrument_source_object_layer.py
```

Standalone optional MVP visibility layer after temporal-timbre object candidates. It reads `temporal_timbre_object_candidate_layer.json` plus optional `instrument_prior_filterbank_layer.json`, `auditory_object_behavior_layer.json`, and `musical_object_performance_layer.json`, then writes `instrument_source_object_layer.json` and `.md`.

It groups existing evidence into explicit source-family object cards such as voice / vocal-like, bass / low-register, drum / percussion, guitar / plucked, keyboard / piano, synth / pad / harmonic, strings / bowed, brass / wind, and FX / texture / tail. These are candidate objects, not verified instrumentation or separated stems. This layer is not connected to default `run_mssl.py` yet.

```text
scripts/validate_instrument_source_object_layer.py
scripts/validate_compact_handoff_instrument_source_objects.py
```

No-audio validators for the source-family object layer and its compact handoff rendering.

```text
scripts/build_auditory_object_behavior_layer.py
```

Standalone optional layer after temporal-timbre object candidates and before musical object performance. It reads `temporal_timbre_object_candidate_layer.json` plus optional profile, OME arrangement contrast, gammatone envelope, and instrument-prior filterbank evidence, then writes `auditory_object_behavior_layer.json` and `.md`. It is not connected to the default `run_mssl.py` chain yet. It describes behavior for existing object candidates only, cannot exceed candidate claim strength, and cannot turn candidate-like language into source certainty.

```text
scripts/build_listening_region_locator_layer.py
```

Builds bounded listening-region locations from an existing full-song profile. It locates structural components such as low-body, transient-plane, foreground-contour, harmonic-ridge, diffuse-tail, noise-texture, spatial-spread, and pressure-peak regions. It does not name instruments, perform source separation, use trained models, or bypass external recognition.

```text
scripts/build_musical_object_performance_layer.py
```

Builds vocal / instrumental / effect-family performance cards. This layer is intentionally not a machine behavior layer. Specific verified family cards require the external family gate. Local source-family candidates may still remain visible as bounded candidate evidence; unverified performance prose must not become confirmed source identity.

Optional standalone input:

```text
--auditory-object-behavior path/to/auditory_object_behavior_layer.json
```

This consumes behavior cards as bounded performance support only. It is not connected to the default `run_mssl.py` chain yet, cannot exceed behavior-card claim strength, and cannot replace external recognition or family-gate permission.

```text
scripts/build_lyric_context_layer.py
```

Builds bounded lyric context from optional local lyric/alignment files plus MSSL vocal, MIDI, and OME anchors. It does not export full lyrics into report-facing handoff.

```text
scripts/build_listening_experience_prompt_with_descriptors.py
```

Descriptor-aware wrapper. It attaches song identity, lyric context, subjective descriptor validation, OME packet material, symbolic timeline MIDI layer, external recognition status, musical object performance layer, compact handoff, and full trace handoff.

Optional standalone input:

```text
--musical-object-performance path/to/musical_object_performance_layer.json
--instrument-source-objects path/to/instrument_source_object_layer.json
```

These let behavior-enriched standalone performance and explicit source-family object layers feed compact handoff rendering without writing them back into the profile. They are optional / standalone and are not default `run_mssl.py` integration.

```text
scripts/render_compact_online_handoff.py
```

Renders the compact online handoff as a report-composer schema: song identity, source-family permission, vocal/lyric anchors, explicit source-family object candidates when available, instrument/source-family performance, optional bounded musical-object behavior support, MIDI/melody/rhythm skeleton, general audio evidence, OME spatial performance state, macro arc, and writing boundaries. Behavior support is timing/action evidence only; it does not create verified source-family certainty or bypass the family gate.

## Song identity contract

Song identity can be supplied directly:

```text
--song-title
--song-artist
--song-album
--song-year
--song-identity-json
```

Or generated in the main flow:

```text
--song-identity-command "python scripts/adapters/run_song_identity_adapter.py --input {input} --output-json {output_json} ..."
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

Main-flow command:

```text
--midi-adapter-command "python scripts/adapters/run_basic_pitch_adapter.py --input {input} --output-json {output_json} ..."
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

Accepted paths:

```text
--external-recognition path/to/recognition_packet.json
--external-recognition-command "python recognizer.py --input {input} --output-json {output_json}"
python scripts/adapters/normalize_external_recognition_packet.py --input-json raw_tool_output.json --output-json recognition_packet.json
python scripts/adapters/run_demucs_adapter.py --input audio.wav --output-json recognition_packet.json --stems-dir path/to/stems
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
-> song identity status / command evidence
-> audio mechanism evidence
-> reconstructed stream / score skeleton
-> MIDI adapter evidence / symbolic timeline MIDI layer
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

Main-run output shape, with optional standalone layer artifacts marked when they are run separately:

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
  ome_gammatone_envelope_layer.json / .md (optional standalone)
  ome_gammatonegram_mid.png (optional standalone)
  ome_gammatonegram_side.png (optional standalone)
  ome_arrangement_contrast_layer.json / .md (optional standalone)
  ome_arrangement_timeline.png (optional standalone)
  ome_arrangement_readable_summary.md (optional standalone)
  listening_region_locator_layer.json / .md (optional standalone)
  instrument_prior_filterbank_layer.json / .md (optional standalone)
  temporal_timbre_object_candidate_layer.json / .md
  instrument_source_object_layer.json / .md (optional standalone)
  auditory_object_behavior_layer.json / .md (optional standalone)
  musical_object_performance_layer.json / .md
  lyric_context_layer.json / .md
  original_song_listening_prompt_input.md
  online_ai_listening_handoff.md
  online_ai_listening_handoff_full_trace.md
```

Generated output files are local artifacts and should not be committed unless explicitly curated.

## Main command examples

Windows:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.mp3"
```

With identity and lyric context:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --song-title "Song title" --song-artist "Artist" --lyrics-file "path\to\lyrics.txt" --lyric-alignment "path\to\lyric_alignment.json"
```

With identity command:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --song-identity-command "python .\scripts\adapters\run_song_identity_adapter.py --input {input} --output-json {output_json} --metadata-command 'ffprobe -v quiet -print_format json -show_format -show_streams {input} > {metadata_json}'"
```

With MIDI adapter command:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --midi-adapter-command "python .\scripts\adapters\run_basic_pitch_adapter.py --input {input} --output-json {output_json} --notes-csv path\to\notes.csv"
```

With Demucs / UVR stem adapter command:

```powershell
python .\scripts\run_mssl.py experience --input "path\to\local_audio.wav" --external-recognition-command "python .\scripts\adapters\run_demucs_adapter.py --input {input} --output-json {output_json} --stems-dir path\to\stems"
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
