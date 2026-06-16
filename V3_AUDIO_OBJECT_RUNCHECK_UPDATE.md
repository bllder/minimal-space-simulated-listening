# V3 Audio Object Runcheck Update

This update adds an executable runcheck layer that combines MSSL's visualized listening-space language with a small audio-evidence layer.

## Added script

`scripts/run_audio_object_runcheck.py`

The script reads a selected WAV clip and generates:

- `outputs/audio_object_runcheck.json`
- `outputs/audio_object_runcheck_report.md`

## What it runs

The script uses Python standard library + numpy only. It computes:

- RMS / peak pressure evidence
- spectral centroid / bandwidth
- low / mid / high energy ratios
- stereo side-ratio / phase-correlation
- spectral-flux onset candidates
- a lightweight HPSS-style harmonic/percussive tendency proxy using median filters

These audio terms are not the main language of the project. They are an evidence layer used to support the visualized listening-field interpretation.

## Object candidates

The runcheck report tracks three candidate auditory objects:

1. `object_01_near_rhythmic_pulse`  
   Near-field recurring pulse / processed rhythmic beat object.

2. `object_02_floating_piano`  
   Farther upper floating piano candidate, treated as a ribbon/surface plus possible distant point.

3. `object_03_vocal_contour`  
   Near-to-mid deformable vocal contour candidate, treated as a high-degree-of-freedom listening object.

These are candidate object tracks, not source separation and not automatic instrument recognition.

## Current 8s run

The script was run on:

`outputs/thz_00m42s_00m50s.wav`

with source label:

`D:\CloudMusic\thz.wav`

absolute window:

`42.00s-50.00s`

## Main result

The 8s clip is best treated as three trackable objects in a visualized listening field:

- a near recurring rhythmic pulse,
- a farther floating piano candidate,
- a near-mid vocal contour candidate.

The runcheck reports top onset candidates and 1s evidence blocks, while keeping the human listening validation at the continuous 8s event level.

## Boundary

This update does not implement source separation, vocal detection, piano recognition, transcription, music theory analysis, or model training.

It only adds a bridge:

`audio evidence → visualized listening field → temporal-spatial auditory object tracking`
