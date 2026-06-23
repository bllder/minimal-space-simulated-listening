# OME Spatial Filter Bank Design Spec

Status: P0 design specification.

This file defines the future OME Spatial Filter Bank contract.

MSSL does not perform traditional true stem separation. It derives receiver-side spatial-band auditory object streams from stereo evidence.

Pipeline target:

```text
stereo audio
-> OME Spatial Filter Bank
-> spatial-band auditory streams
-> OME Binaural Cue Validation
-> per-stream analysis
-> perceptual metadata packet
-> online AI handoff
```

P0 stream IDs:

```text
center_low_impact
center_low_sustain
center_mid_lead
side_harmonic_space
wide_diffuse_texture
residual_unassigned
```

The full design will be expanded from `docs/ome_spatial_filter_bank_reading_notes.md` before any Python implementation is added.
