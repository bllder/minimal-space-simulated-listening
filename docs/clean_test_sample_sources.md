# Clean Test Sample Sources

This document records which public audio sample pools may be used for MSSL validation without committing copyrighted local songs or comment-derived outputs into the repository.

The goal is not to train taste.

The goal is to test whether MSSL can turn audio evidence into a stable O/M/E mapping packet and track auditory objects across time.

---

## Core rule

Use public sample pools for reproducible tests.

Do not commit:

```text
copyrighted commercial songs
local music-library files
scraped comments
song-specific P4 profiles
generated stems
generated MIDI
generated reports from copyrighted songs
large datasets or archives
```

The repository may contain:

```text
small metadata notes
source links
license notes
test-case selection rules
expected output schemas
```

Audio files and generated artifacts stay local unless a specific file is legally safe, small, and intentionally curated.

---

## 1. FMA / Free Music Archive dataset

Status: **approved public test sample pool**.

Reference:

- https://github.com/mdeff/fma

MSSL use:

```text
public demo sample candidates
cross-style validation
baseline feature extraction checks
object-tracking consistency checks
report reproducibility tests
```

Allowed use:

```text
select a small number of tracks with clear licenses
record track IDs and license metadata
run local MSSL validation
commit only schemas, scripts, and small non-audio notes
```

Forbidden use:

```text
commit full dataset
commit downloaded audio by default
commit generated outputs by default
ignore per-track license terms
use genre labels as MSSL ontology
train taste or preference scoring
```

MSSL interpretation boundary:

```text
FMA genre / tag metadata can be used as external reference labels.
They do not define what the auditory object is.
They do not decide whether a listening report is correct.
```

Priority: **first public sample pool**.

Reason: known MIR dataset, open research use, useful for reproducible baseline testing.

---

## 2. MTG-Jamendo dataset

Status: **approved public test sample pool with license caution**.

Reference:

- https://mtg.github.io/mtg-jamendo-dataset/

MSSL use:

```text
mood / theme / instrument label comparison
cross-genre test cases
optional external label sanity check
public validation candidate pool
```

Allowed use:

```text
select tracks with license metadata reviewed
use tags as external comparison only
run local analysis
record which tags were compared against MSSL evidence
```

Forbidden use:

```text
use tags as direct MSSL report language
use mood/theme labels as truth oracle
commit downloaded tracks by default
ignore non-commercial or share-alike restrictions
turn dataset labels into taste scoring
```

MSSL interpretation boundary:

```text
MTG-Jamendo labels can help test whether MSSL output contradicts obvious public tags.
They cannot replace O/M/E mapping, object tracking, or human report review.
```

Priority: **second public sample pool**.

Reason: useful tags for comparison, but stronger license and label-contamination caution is needed.

---

## Local folder policy

Use local ignored folders for downloaded data and generated outputs:

```text
data/
outputs/
configs/
```

Recommended local layout:

```text
data/public_samples/fma/
data/public_samples/mtg_jamendo/
outputs/public_sample_runs/
configs/local_sample_selection/
```

These paths are examples for local work. They should remain ignored unless a future PR explicitly adds a tiny, legally safe sample manifest.

---

## Safe manifest format

If a public test manifest is later added, use metadata only:

```json
{
  "sample_id": "example_track_id",
  "source": "FMA or MTG-Jamendo",
  "title": "metadata title if safe",
  "artist": "metadata artist if safe",
  "license": "license string from source",
  "source_url": "source page or dataset reference",
  "local_audio_path": "not committed",
  "mssl_test_reason": "why this sample is useful",
  "allowed_public_output": false
}
```

Do not include lyrics, scraped comments, private notes, or copyrighted-song-derived report language in the manifest.

---

## Review checklist before publishing any sample result

```text
1. Is the source license clear?
2. Is the audio itself allowed to be redistributed?
3. Is the output derived from a copyrighted track?
4. Does the report contain style labels or listener-comment terms that could contaminate MSSL language?
5. Is the output a general schema/example, or a single-song evaluation artifact?
6. Can the same validation be described with metadata only?
```

Default answer: keep audio and generated song-specific outputs local.
