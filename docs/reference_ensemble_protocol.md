# Reference Ensemble Protocol

Status: protocol for local probe generation and MSSL structure checking.

This protocol defines a small, controllable reference ensemble for MSSL.
It is inspired by the play-listen-see-compare loop used in interactive music labs, but it does not import those projects as dependencies.

The goal is not to clean a large dataset.
The goal is to create a small local band of known probes so MSSL can compare:

```text
playable event
→ audible probe
→ music-theory / arrangement label
→ signal evidence
→ O/M/E mapping
→ scene graph candidate
```

---

## Why this layer exists

The current MSSL chain can already run:

```text
audio file
→ audio_evidence_packet.json
→ ome_mapping_packet.json
→ object_candidate_packet.json
→ object_track_packet.json
→ auditory_scene_graph_packet.json
```

However, a scene graph packet is not easy to read by itself.
A reference ensemble gives the system known inputs with known intent.

Instead of asking:

```text
What is this song?
```

this layer asks:

```text
If we generate a known chord, pulse, texture, or stereo spread,
which evidence fields and scene roles does MSSL produce?
```

This provides a controlled bridge between hearing, theory, samples, and numbers.

---

## Core object: reference probe

A reference probe is a small generated audio/MIDI test object.

Each probe may include:

```text
probe.wav                    local generated audio, ignored by git
probe.mid                    local generated MIDI, ignored by git
probe_manifest.json          local generated probe description
expected_mapping.json        local generated expected MSSL role hints
mssl_output/                 local generated pipeline outputs
reference_probe_comparison_packet.json
```

Generated files live under `outputs/` by default and must not be committed.
The repository only stores scripts, protocol docs, and manifest templates.

---

## First probe families

The first local ensemble should stay small and controllable:

```text
single_note_C4
major_triad_C4
arpeggio_C_major
click_grid_120bpm
low_pulse_80hz
filtered_noise_texture
stereo_spread_noise
harmonic_layer_plus_pulse
```

These are not musical works.
They are reference signals.

---

## Four-way mapping

Each probe should expose four levels of meaning.

### 1. Audible sample

The generated WAV is the thing the user can hear.
It should be short, local, and reproducible.

### 2. Music-theory / arrangement label

For pitched probes, the manifest can include:

```text
notes
chord
intervals
register
arrangement_role
```

For non-pitched probes, the manifest can include:

```text
pulse pattern
texture type
stereo motion
pressure body
arrangement_role
```

### 3. Expected signal evidence

The expected mapping file should use qualitative expectations, not hard numeric truth:

```text
onset_density: low / medium / high
harmonic_stability: low / medium / high
spectral_density: low / medium / high
stereo_width: low / medium / high
pressure_proxy: low / medium / high
```

These expectations are hints for checking the pipeline.
They are not model labels.

### 4. Expected MSSL scene roles

Expected roles should use existing MSSL candidate names when possible:

```text
harmonic_layer_candidate
texture_mass_candidate
transient_event_candidate
rhythmic_pulse_candidate
pressure_body_candidate
receiver_spread_layer_candidate
```

A match means the current pipeline surfaced a compatible candidate.
It does not mean the system has confirmed a real sound source.

---

## Boundary with MIDI

MIDI is useful here because it gives a compact, explicit description of intended note events.

MIDI in this protocol means:

```text
probe score
note-event control signal
playable reference object
```

MIDI does not mean:

```text
full transcription truth
complete arrangement truth
source identity
human listening report
```

A generated probe may include both WAV and MIDI.
The WAV is analyzed by MSSL.
The MIDI is a reference score for human and future UI comparison.

---

## Boundary with Basic Pitch and other audio-to-MIDI adapters

Basic Pitch or any future audio-to-MIDI adapter can later be connected as an optional adapter.
It must remain separate from the generated reference ensemble.

Generated reference probes answer:

```text
What did we intentionally play?
```

Audio-to-MIDI adapters answer:

```text
What note events might be inferred from a real audio file?
```

These are different directions and must not be collapsed.

---

## Boundary with report generation

This layer stops before final report generation.

Allowed output:

```text
reference_probe_comparison_packet.json
```

Not allowed by default:

```text
listening_report.md
public review language
music taste judgment
human-calibrated language
song interpretation
```

The comparison packet may say that a probe produced a compatible scene role.
It must not turn that into final listening prose.

---

## Minimal local run shape

The intended local run is:

```text
scripts/run_reference_probe_bank.py
→ generated probes under outputs/reference_probe_bank/
→ MSSL baseline pipeline for each probe
→ reference_probe_comparison_packet.json
→ stop before report
```

The generated comparison packet should make the stopping point explicit:

```json
{
  "report_boundary": {
    "stops_before_listening_report": true,
    "reason": "reference comparison is not human-calibrated listening language"
  }
}
```

---

## What this does not replace

The reference ensemble does not replace:

```text
human listening
real audio smoke tests
public sample manifests
optional adapters
human calibration
final report policy
```

It provides a controlled calibration bridge so that MSSL can be checked against known, playable structures before moving into real songs or reports.
