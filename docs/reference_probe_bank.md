# Reference Probe Bank Runner

Status: local engineering tool.

The runner creates a small generated reference ensemble and sends each probe through the current MSSL baseline chain.
It stops at the comparison packet and does not generate a listening report.

---

## What it generates

Default command:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_reference_probe_bank.py
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_reference_probe_bank.py
```

Default output root:

```text
outputs/reference_probe_bank/
```

Each probe folder contains local generated artifacts:

```text
probe.wav
probe.mid
probe_manifest.json
expected_mapping.json
mssl_output/
reference_probe_comparison_packet.json
```

The bank root also writes:

```text
reference_probe_bank_run.json
```

All generated outputs are local artifacts and must stay ignored by git.

---

## Default probe list

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

These probes are not a music dataset.
They are a controllable reference band for checking how MSSL maps known signal structures into scene graph candidates.

---

## Run one probe only

```powershell
.\.venv\Scripts\python.exe .\scripts\run_reference_probe_bank.py --probe major_triad_C4
```

---

## Generate only, without running MSSL pipeline

```powershell
.\.venv\Scripts\python.exe .\scripts\run_reference_probe_bank.py --generate-only
```

This is useful when checking the generated WAV/MIDI files before running the full baseline chain.

---

## What the comparison checks

For each probe, the runner compares expected role hints with observed scene graph candidate names.

Expected roles use existing MSSL candidate names such as:

```text
harmonic_layer_candidate
texture_mass_candidate
transient_event_candidate
rhythmic_pulse_candidate
pressure_body_candidate
receiver_spread_layer_candidate
```

The comparison packet reports:

```text
matched_roles
missing_roles
observed_node_summaries
report_boundary
```

A structural match is not ground truth.
It only means the current baseline pipeline surfaced compatible candidate names.

---

## Where it stops

The runner stops before final report generation.

It is allowed to create:

```text
reference_probe_comparison_packet.json
```

It is not allowed to create:

```text
listening_report.md
public review language
music taste judgment
human-calibrated listening prose
```

This is intentional. The reference ensemble is a bridge between audible probes, theory labels, generated samples, signal values, and MSSL scene roles. It is not the final human-readable listening layer.

---

## Dependency note

The probe generator itself uses only the Python standard library.

Running the full pipeline still calls the baseline evidence adapter, so the local environment needs the same dependency as the minimal smoke runner:

```powershell
.\.venv\Scripts\python.exe -m pip install librosa
```
