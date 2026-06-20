# Full Song Structural Pipeline

Project: **Minimal Space for Simulated Listening**  
Codename: **Groove Ear / 给 AI 耳朵**  
Script: `scripts/run_full_song_analysis.py`  
Status: structural front half of the current experience pipeline

---

## 1. Purpose

This document defines how MSSL moves from the earlier 5-10 second validation clip into a local full-song structural run.

Target use:

```text
Input: 3-30 minute WAV song
Output:
  whole-song information
  estimated BPM and beat / bar-like grid
  audio-derived structural segments
  per-segment audio evidence
  per-segment O/M/E spatial dynamics
  per-segment auditory object candidates
  structural inspection material for downstream handoff
```

This is not a return to conventional music information retrieval. The script keeps common audio terms as evidence, but the project ontology remains receiver-side simulated listening.

The final human-facing close-listening text is not produced here. It is produced only after:

```text
full_song_profile.json
-> listening_experience_evidence_pack.json
-> critical_listening_brief.json
-> online_ai_listening_handoff.md
-> bounded LLM close-listening criticism
```

---

## 2. Not one-second validation

The old validation path used one-second and sub-second windows to inspect whether the mapping packet could exist.

Full-song analysis uses:

```text
structural segment = main evidence unit
frame evidence = internal support layer
beat / bar grid = rhythm reference layer
```

A one-second block may still be useful for debugging, but it must not become the main listening unit.

---

## 3. Runtime stages

```text
1. Read full PCM WAV
2. Preflight: path / sample rate / channels / duration
3. Extract frame evidence from the whole track
4. Estimate BPM and beat grid from onset evidence
5. Detect structural segment boundaries from novelty curves
6. Aggregate each segment into audio evidence
7. Translate segment evidence into O/M/E proxies
8. Build auditory object candidates
9. Track relative spatial change from segment to segment
10. Write JSON structural profile
11. Downstream experience pipeline builds evidence pack, critical brief, and online-AI handoff
```

---

## 4. Audio evidence retained

The full-song script keeps common audio information because the user needs general song structure evidence as well as MSSL listening-space evidence.

Current evidence fields include:

```text
RMS / peak / dBFS
zero-crossing rate
spectral centroid
spectral bandwidth
spectral rolloff
spectral flatness
low / mid / high ratio
fine spectral band ratios
spectral flux
onset strength
estimated BPM
beat times
bar-like times
stereo side ratio
phase correlation
left-right balance
```

These are mechanism outputs. They are not the project ontology.

---

## 5. O/M/E segment translation

Each segment receives a compact O/M/E mapping:

```text
O-space:
  modeled source-side wave candidate
  emission strength
  directionality center
  emission shape

M-domain:
  pressure transfer
  spread transform
  temporal continuity
  transient transfer
  masking risk

E-space:
  left_right
  near_far
  high_low
  perceived_pressure
  perceived_width
  perceived_spread
  perceived_motion
  envelopment
```

The segment also records `relative_to_previous_segment`, so downstream layers can describe motion across the song rather than freezing each segment as an isolated picture.

---

## 6. Object candidates

The full-song structural profiler uses broad object candidates:

```text
object_01_near_rhythmic_pulse
object_02_low_end_body
object_03_harmonic_layer
object_04_vocal_contour_candidate
object_05_noise_or_texture_mass
```

These are not confirmed instruments.

They are listening-space hypotheses supported by audio evidence.

The next mainline extension should turn these labels into bounded object behavior / personality signals before the critical brief reads them.

---

## 7. Style profile boundary

The script outputs style candidates such as:

```text
electronic_or_beat_driven
rock_or_band_driven
ambient_or_spatial
vocal_song_candidate
noise_texture_or_experimental
```

These are heuristic style profiles, not authoritative genre labels.

The correct interpretation is:

```text
The audio evidence resembles a style behavior.
```

not:

```text
The system knows the genre.
```

---

## 8. Local command

Normal users should start from `scripts/run_mssl.py`. Use `run_full_song_analysis.py` directly only for structural profiling.

Windows example:

```powershell
.\.venv\Scripts\python.exe scripts\run_full_song_analysis.py --input "path\to\local_audio.wav" --output-dir outputs
```

Windows optional segment tuning:

```powershell
.\.venv\Scripts\python.exe scripts\run_full_song_analysis.py --input "path\to\local_audio.wav" --output-dir outputs --min-segment-seconds 8 --max-segment-seconds 45
```

macOS / Linux example:

```bash
./.venv/bin/python scripts/run_full_song_analysis.py --input "path/to/local_audio.wav" --output-dir outputs
```

macOS / Linux optional segment tuning:

```bash
./.venv/bin/python scripts/run_full_song_analysis.py --input "path/to/local_audio.wav" --output-dir outputs --min-segment-seconds 8 --max-segment-seconds 45
```

Primary output:

```text
outputs/<song>/<song>_full_song_profile.json
```

If Markdown inspection material is produced or retained by a wrapper, it is local structural inspection only, not final listening criticism.

---

## 9. Next extension points

Source separation and vocal locking remain optional evidence adapters.

They should enter later as:

```text
optional stem evidence
-> object candidate support / weakening
-> E-space motion evidence
```

They must not replace the MSSL object model.

Mainline next step:

```text
object candidates
-> object personality / behavior layer
-> critical listening brief
```
