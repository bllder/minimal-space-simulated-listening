# Public Sample Manifest Template

Status: template only.

This file defines the public validation sample slots for MSSL.
It does not include audio files, generated outputs, comments, or song-specific profiles.

## Rules

```text
Do not commit audio files.
Do not commit generated song outputs by default.
Use only samples with reviewed source license metadata.
Keep local downloads under ignored local folders.
Use public tags only as external comparison notes, not as MSSL ontology.
```

## Local folders

```text
data/public_samples/fma/
data/public_samples/mtg_jamendo/
outputs/public_sample_runs/
```

These folders are local working paths and should stay ignored by git.

## Target slots

```text
FMA: 3 samples
MTG-Jamendo: 2 samples
```

## Manifest fields

Each selected sample should record:

```text
sample_id
source
dataset_track_id
title
artist
license
source_url
local_audio_path
committed_audio
allowed_public_output
mssl_test_reason
selection_status
```

## Pending sample slots

```text
FMA_PENDING_001 — baseline evidence smoke check
FMA_PENDING_002 — object candidate diversity smoke check
FMA_PENDING_003 — stereo proxy smoke check
MTG_JAMENDO_PENDING_001 — external tag boundary check
MTG_JAMENDO_PENDING_002 — public sample comparison check
```

Actual sample IDs should be filled only after source and license review.
