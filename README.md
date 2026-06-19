# Minimal Space for Simulated Listening

**Minimal Space for Simulated Listening (MSSL)** is a structural-only audio project that maps local WAV evidence into bounded O/M/E listening-space packets and summaries.

> We do not train taste. We build a minimal spatiotemporal domain for simulated listening.  
> 我们不训练品味；我们保留模拟听觉所需的最小时空结构。

## O/M/E frame

```text
O = source-centered wave-expansion space
M = source-to-receiver spatiotemporal mapping domain
E = receiver-centered auditory modeling space
```

MSSL treats sound as a bounded propagation relation from **O** through **M** into **E**, not as a single-point waveform-to-label conversion.

## Visual overview

The two diagrams below are the human entry point for the project: one explains the modeling frame, and one explains the current runtime frame.

### Modeling framework of sound / 声的建模框架

![Modeling Framework of Sound](./声的建模框架图解.png)

### Overall runtime framework / 总程序运行框架

![Overall Runtime Framework](./总体框架流程图.png)

For the detailed execution-rule diagram, see [`docs/detailed_runtime_flow.md`](docs/detailed_runtime_flow.md).

## Structural-only boundary

The repository currently stops at structural evidence and structural summaries.

It does **not** produce or claim:

- taste judgment
- genre truth
- emotion truth
- singer identity
- instrument identity
- lyric recognition or ASR
- source-separation truth
- human-calibrated listening reports
- music generation

Any generated Markdown under `outputs/` is a local inspection artifact unless a future task explicitly promotes a curated example.

External adapters are optional and not part of the default structural-only pipeline. See `docs/optional_adapters.md`.

## Current minimal chain

The current minimal structural chain is:

```text
local PCM WAV / local synthetic probe
-> audio evidence
-> O/M/E mapping packet
-> object candidate packet
-> object track packet
-> auditory scene graph packet
-> structural summary
-> STOP before human calibration or listening-report generation
```

A separate manual bridge can be explicitly invoked after a full-song profile exists:

```text
MSSL segment evidence
-> critical_listening_brief
-> external LLM close-listening criticism
```

This bridge is not part of the default structural-only pipeline and does not generate a final review inside MSSL.

Default dependency file:

```text
requirements.txt
```

It is intentionally minimal and currently contains only `numpy`.

Optional dependency notes live under `requirements-optional/`.

## Run locally

Create and activate a project-local virtual environment, then install the default dependency file:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Smoke-check the current Python entry points without writing outputs:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_full_song_analysis.py --help
.\.venv\Scripts\python.exe .\scripts\run_music_understanding_summary.py --help
.\.venv\Scripts\python.exe .\scripts\build_critical_listening_brief.py --help
```

Run a full-song structural pass on a local PCM WAV:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_full_song_analysis.py `
  --input "path\to\local_audio.wav" `
  --output-dir outputs
```

After packet-chain outputs exist in a run directory, generate the structural understanding summary:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_music_understanding_summary.py `
  --run-dir outputs\your_run_dir
```

When explicitly needed for external close-listening writing, build a critical listening brief from the full-song profile:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_critical_listening_brief.py `
  --input outputs\your_run_dir\your_song_full_song_profile.json `
  --output-dir outputs\your_run_dir
```

This writes `critical_listening_brief.json` and `critical_listening_prompt_input.md` for manual use with an external LLM. It does not read audio, run ASR, identify singers or instruments, assert genre or emotion truth, or generate the final music criticism.

macOS / Linux use the same commands with `./.venv/bin/python`.

## Outputs policy

Do not commit generated outputs or local media:

```text
outputs/
*.wav
*.mp3
*.m4a
*.flac
.venv/
__pycache__/
```

The repository should remain a readable minimal project: source scripts, compact docs, default requirements, and no local run artifacts.
