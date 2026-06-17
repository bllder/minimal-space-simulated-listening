# Portable Path Audit

This audit records project-local path assumptions that can prevent a cloned repository from running from an arbitrary folder.

## Principle

The repository should not require a specific drive letter or user-local directory.

Allowed:

```text
<project-root>
<legacy-project-path>
path/to/local_audio.wav
path\to\local_audio.wav
outputs/<input-stem>/...
```

Avoid in committed runtime instructions:

```text
D:\minimal-space-simulated-listening
D:\groove-ear
D:\CloudMusic\...
```

---

## Findings

### Running code

No active script was found to read from or write to a hardcoded `D:\...` path.

The scripts use command-line arguments such as `--input`, `--output-dir`, or `--source-label`; these can point to any local path.

One argparse help string in `scripts/run_audio_object_runcheck.py` used a `D:\CloudMusic\...` example. This is a help-text example, not runtime behavior. It should be changed in a follow-up script-only edit to avoid confusion.

### Execution docs

The following docs contained machine-specific examples and were generalized in this branch:

```text
AGENTS.md
references/legacy_index.md
docs/migration_log.md
docs/librosa_baseline_evidence.md
docs/full_song_analysis_pipeline.md
V3_AUDIO_OBJECT_RUNCHECK_UPDATE.md
V4_FULL_SONG_ANALYSIS_UPDATE.md
```

### README

`README.md` still contains an older Windows environment section with a machine-specific venv path. It should be updated in a README-only follow-up to use:

```text
<project-root>/.venv
```

and OS-specific examples:

```powershell
.\.venv\Scripts\python.exe
```

```bash
./.venv/bin/python
```

---

## Runtime rule going forward

Scripts must not assume the project lives on any specific drive or folder.

Docs should say:

```text
Run from the project root.
The audio input may be anywhere on the local machine.
Generated outputs should go under outputs/ by default.
```

Legacy references should say:

```text
<legacy-project-path>
```

instead of naming a user-local path.
