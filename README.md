# Minimal Space for Simulated Listening

**Minimal Space for Simulated Listening (MSSL)** builds a minimal simulation space between audio evidence and human-readable listening experience.

> We do not train taste. We build a minimal spatiotemporal domain for simulated listening.  
> 我们不训练品味；我们构造模拟听觉所需的最小时空与语言承接结构。

## Project goal

MSSL is not only O/M/E packet generation. O/M/E is the spatial simulation layer; the human-facing layer must also accept bounded aesthetic and external context.

Current target path:

```text
local PCM WAV
-> structural audio evidence
-> reconstructed stream / score layer
-> OME Spatial Filter Bank runtime layer
-> temporal-timbre object candidate layer
-> listening-experience evidence pack
-> descriptor-gated OME packet staging
-> compact online AI handoff + full audit trace
-> bounded close-listening criticism by an online AI account
```

The compact handoff must foreground evidence-bounded auditory object support before broad descriptive language. Object-family candidates should be formed from time-frequency-timbre continuity and optional external timbre / stem / transcription evidence, then mapped into receiver-side O/M/E space. OME field packets are spatial mapping support, not object identity by themselves.

MSSL does not need to rebuild every music-recognition capability itself. External model outputs, optional adapters, comments, reviews, MIR notes, and user aesthetic material may be introduced as bounded context. MSSL organizes claim boundaries, evidence traceability, and handoff structure.

The default project does **not** run a local LLM. The local pipeline prepares an uploadable compact handoff file for an online AI account.

## O/M/E frame

```text
O = source-centered wave-expansion space
M = source-to-receiver spatiotemporal mapping domain
E = receiver-centered auditory modeling space
```

MSSL treats sound as a bounded propagation relation from **O** through **M** into **E**, not as a single-point waveform-to-label conversion.

The O/M/E layer is not spatial-audio rendering and not a generic audio-feature table. It builds a receiver-side perceptual representation layer for AI listening handoff.

## One-command entry point

Use this first:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py `
  --input "path\to\local_audio.wav" `
  --output-dir outputs
```

By default this runs `experience` mode and writes:

```text
online_ai_listening_handoff.md
online_ai_listening_handoff_full_trace.md
reconstructed_stream_score_layer.md
ome_spatial_filter_bank_layer.json / .md
temporal_timbre_object_candidate_layer.json / .md
subjective_descriptor_proxy_layer.json / .md
ome_stream_descriptor_packets.json / .md
```

`online_ai_listening_handoff.md` is the compact online-AI input. The object layer must follow the consolidated boundary in `docs/b_mssl_scope_boundary.md`: object candidates come from time-frequency-timbre evidence and bounded source-family hypotheses before behavior language or OME spatial mapping is used.

## Documentation map

```text
docs/a_professional_term_index.md
docs/b_mssl_scope_boundary.md
docs/c_online_handoff_translation.md
docs/d_adapter_gate.md
docs/e_runtime_entrypoints.md
docs/f_validation_samples.md
docs/g_project_log.md
```

Do not add standalone docs unless the topic cannot be folded into A/B/C/D/E/F/G.

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
