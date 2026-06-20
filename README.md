# Minimal Space for Simulated Listening

**Minimal Space for Simulated Listening (MSSL)** builds a minimal simulation space between audio evidence and human-readable listening experience.

> We do not train taste. We build a minimal spatiotemporal domain for simulated listening.  
> 我们不训练品味；我们构造模拟听觉所需的最小时空与语言承接结构。

## Project goal

MSSL is not only O/M/E packet generation. O/M/E is the spatial simulation layer; the human-facing layer must also accept aesthetic and external context.

Current target path:

```text
local PCM WAV
-> structural audio evidence
-> O/M/E listening-space simulation
-> object / relation / scene evidence
-> listening-experience evidence pack
-> critical listening brief
-> aesthetic context handoff
-> online AI handoff
-> bounded close-listening criticism
```

MSSL does not need to rebuild every music-recognition capability itself. External model outputs, optional adapters, online AI accounts, local LLM backends, lyrics, comments, reviews, MIR notes, and user aesthetic material may be introduced as bounded context. MSSL organizes claim boundaries, evidence traceability, and handoff structure.

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

## Boundaries

The default structural layer does **not** produce or claim truth labels for:

- taste judgment
- genre truth
- emotion truth
- singer identity
- instrument identity
- lyric recognition or ASR
- source-separation truth
- music generation

The listening-experience layer may use genre-like, emotion-like, or instrument-family language only when bounded by evidence, adapter output, online AI reasoning, user aesthetic context, or an explicit backend stage. These words belong in the language/context layer, not as unbounded structural truth.

Any generated Markdown under `outputs/` is a local inspection artifact unless a future task explicitly promotes a curated example.

External adapters are optional and not part of the minimal default dependency set. See `docs/optional_adapters.md`.

## One-command entry point

Use this first:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py `
  --input "path\to\local_audio.wav" `
  --output-dir outputs
```

By default this runs `experience` mode:

```text
WAV
-> full_song_profile.json
-> listening_experience_evidence_pack.json
-> critical_listening_brief.json
-> original_song_listening_prompt_input.md
-> online_ai_listening_handoff.md
```

If you have human/aesthetic context, add it explicitly:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py `
  --input "path\to\local_audio.wav" `
  --playlist-context "没有意义" `
  --aesthetic-context "path\to\aesthetic_seed.json" `
  --external-context "path\to\lyrics_or_review.txt"
```

If you do not have a local LLM or API key, use this file:

```text
online_ai_listening_handoff.md
```

Copy or upload it to an online AI account. It is the MSSL handoff that replaces sending the audio file. Ask the online AI to write bounded close-listening criticism from it.

Advanced optional path: to generate final prose locally, provide an LLM command that reads prompt text from stdin and writes Markdown to stdout:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py `
  --input "path\to\local_audio.wav" `
  --output-dir outputs `
  --llm-command "your-local-llm-command"
```

With `--llm-command`, the pipeline writes:

```text
original_song_close_listening_criticism.md
```

Other modes:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py structural --input "path\to\local_audio.wav"
.\.venv\Scripts\python.exe .\scripts\run_mssl.py smoke --generate-synthetic
```

For script status and cleanup notes, see [`docs/scripts_inventory.md`](docs/scripts_inventory.md).

## Aesthetic context handoff

The main human-language correction is:

```text
aesthetic context first
MSSL structure second
LLM close-listening last
```

Do not poetically interpret playlist names before classification. For example:

```text
神圣骨头 = Sacred Bones Records label entry
Starless = King Crimson "Starless" version/material research
Test.py / Math AI = test/probe set
```

See [`docs/aesthetic_context_handoff.md`](docs/aesthetic_context_handoff.md).

## Listening-experience claim layers

The current experience pipeline organizes these bounded claim layers:

```text
source-family / instrument-family evidence
melody or pitch-contour evidence
vocal-object locking evidence
style-behavior hypotheses
affective-listening hypotheses
```

It must not treat stems as instrument truth, style candidates as genre truth, vocal objects as singer identity, or affective tendencies as emotion truth. But it may translate these bounded claims into readable music-listening language when the handoff has adequate context.

`object_personality_layer.json` is experimental only and runs only with:

```text
--experimental-object-personality
```

## Current structural chain

The structural chain is:

```text
local PCM WAV / local synthetic probe
-> audio evidence
-> O/M/E mapping packet
-> object candidate packet
-> object track packet
-> auditory scene graph packet
-> structural summary
```

Language simulation continues after this chain in `experience` mode.

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

Smoke-check entry points without writing music outputs:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py --help
.\.venv\Scripts\python.exe .\scripts\run_mssl.py smoke --generate-synthetic
```

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
