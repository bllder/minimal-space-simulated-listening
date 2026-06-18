# Auditory Hypothesis Fitting Runner

Status: minimal structural-only runner.

This runner adds the first implementation for:

```text
object_candidate_packet.json
-> auditory_hypothesis_packet.json
```

It does not change the smoke runner, reference probe bank, temporal-spatial tracker, auditory scene graph, or music understanding summary layer.

## Script

```text
scripts/run_auditory_hypothesis_fitting_baseline.py
```

Required input:

```text
object_candidate_packet.json
```

Optional sibling inputs, read only when present next to the object candidate packet:

```text
ome_mapping_packet.json
audio_evidence_packet.json
```

Default output:

```text
auditory_hypothesis_packet.json
```

## Run

```powershell
.\.venv\Scripts\python.exe .\scripts\run_auditory_hypothesis_fitting_baseline.py `
  --input "outputs\<input-stem>\object_candidate_packet.json"
```

Optional explicit output path:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_auditory_hypothesis_fitting_baseline.py `
  --input "outputs\<input-stem>\object_candidate_packet.json" `
  --output "outputs\<input-stem>\auditory_hypothesis_packet.json"
```

This script uses only the Python standard library.

## Candidate To Hypothesis Mapping

```text
harmonic_layer_candidate -> sustained_layer
transient_event_candidate -> transient_event
texture_mass_candidate -> texture_mass
pressure_body_candidate -> pressure_body
receiver_spread_layer_candidate -> receiver_spread_field
rhythmic_pulse_candidate -> rhythmic_anchor
```

The runner fails closed on unknown candidate types instead of inventing new structural ontology.

## Hypothesis Fields

Each hypothesis contains:

```text
hypothesis_id
candidate_source
hypothesis_type
fit_score
tracking_permission
supported_by
not_supported_by
confidence_reason
downstream_use
```

`fit_score` is bounded structural support. It combines candidate activation, candidate confidence, and the count of structural O/M/E support fields already present in the object candidate packet.

`tracking_permission` is one of:

```text
allowed
weak_allowed
blocked
```

This permission only marks whether a hypothesis may be useful as a later tracking input. It does not run tracking.

`downstream_use` is advisory only and must not trigger report generation, tracking execution, scene graph generation, or listening-report language.

## Boundary

The runner is structural-only.

It does not:

- generate a listening report
- perform human calibration
- read or use comment data
- make genre, taste, or emotion claims
- identify instruments or singers
- run lyrics, ASR, or semantic-content recognition
- generate music
- modify existing tracking, scene graph, smoke, reference, or summary scripts
