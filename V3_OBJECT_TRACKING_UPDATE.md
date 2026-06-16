# V3 Object Tracking Update

This working copy updates the previous V2.2 validation-scale revision into a V3 temporal-spatial auditory object tracking draft.

## Main change

The report no longer treats the 8-second clip as only a field of proxies. It now adds candidate trackable listening objects:

1. `object_01_near_rhythmic_pulse` — near-field rhythmic pulse / beat object
2. `object_02_floating_piano` — farther floating piano candidate, including a possible distant point
3. `object_03_vocal_contour` — near-to-mid flexible vocal contour candidate

These labels are human-guided listening labels. They are not source separation, not automatic instrument recognition, and not automatic voice recognition.

## Updated files

- `scripts/run_first_validation.py`
- `outputs/baseline_features.json`
- `outputs/mapping_packet.json`
- `outputs/listening_report.md`
- `docs/temporal_spatial_object_tracking.md`
- `docs/migration_log.md`

## Preserved files

- `outputs/thz_00m42s_00m50s.wav` remains the selected 8-second validation clip.

## Principle

MSSL uses visual-spatial language as the primary representation of listening:

```text
visualized listening field
→ perceptual interval
→ object slot
→ object track
→ listening scene graph
```

Audio terminology and music theory should be attached later as evidence layers, after the object-tracking framework is stable.
