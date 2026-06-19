# Scripts Inventory

Status: current entry-point cleanup for the listening-experience phase.

## Primary entry point

Use this first:

```text
scripts/run_mssl.py
```

Default mode:

```text
experience
```

It runs the complete current project path for users without a local LLM or API:

```text
WAV
-> structural profile
-> listening-experience evidence pack
-> technical prompt input
-> online AI handoff Markdown
```

The main human-facing local artifact is:

```text
online_ai_listening_handoff.md
```

Copy or upload that file to an online AI account to generate the final song listening analysis.

## Active scripts

These scripts are currently useful.

```text
scripts/run_mssl.py
```

Single human entry point. Use this for normal work.

```text
scripts/run_listening_experience_pipeline.py
```

Continuation pipeline. It connects full-song structural analysis to listening-experience handoff generation. It can also call an external LLM command when configured, but that is not required for the default online-AI workflow.

```text
scripts/build_listening_experience_prompt.py
```

Builds the evidence pack, technical prompt input, and online-AI handoff file for the language simulation layer.

```text
scripts/run_full_song_analysis.py
```

Full-song structural profiler. Still useful as the structural front half of the experience pipeline.

```text
scripts/run_music_understanding_summary.py
```

Builds structural summaries from packet-chain outputs.

```text
scripts/run_minimal_pipeline_smoke.py
```

Engineering smoke runner for packet-chain validation.

## Support-stage scripts

These are useful as internal stages or diagnostics, but should not be the normal human entry point.

```text
scripts/run_librosa_baseline_evidence.py
scripts/run_mechanism_to_ome_baseline.py
scripts/run_object_candidate_baseline.py
scripts/run_auditory_hypothesis_fitting_baseline.py
scripts/run_temporal_spatial_object_tracking_baseline.py
scripts/run_auditory_scene_graph_baseline.py
scripts/render_readable_structural_summary.py
```

## Validation / diagnostics

Useful for testing, not normal use.

```text
scripts/run_reference_probe_bank.py
scripts/run_audio_object_runcheck.py
```

## Legacy / deprecated entry point

```text
scripts/run_first_validation.py
```

This is an early validation runner. Keep temporarily for historical comparison, but do not use it as the current entry point.

## Cleanup rule

Do not add new top-level runner scripts unless they are wired through `scripts/run_mssl.py` or replace an existing entry point.
