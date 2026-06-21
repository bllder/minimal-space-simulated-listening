# F. Validation and Samples

Status: consolidated validation, sample-selection, and early-loop history.

Use this file to understand what validation exists and what kind of test material is allowed. Do not use it as current runtime architecture.

Consolidated from:

- `baseline_replay_log.md`
- `implementation_plan.md`
- `first_validation_loop.md`
- `public_sample_selection.md`
- `clean_test_sample_sources.md`

## Current purpose

Validation material exists to test whether MSSL can turn audio evidence into stable O/M/E mapping and object-tracking support.

It is not for:

```text
taste training
style scoring
report-language training
committing local song outputs
```

## Early validation loop

The first validation loop was:

```text
hypothesis
-> minimal implementation
-> output result
-> human listening judgment
-> fix fields / fix model
```

The early one-second validation path is historical. It helped compare baseline audio features against mapping-packet descriptions, but it is not the current full-song runtime.

## Historical first-script goal

The first script only asked:

```text
Can mapping_packet describe what is heard better than a plain audio feature table?
```

It did not try to build the current full-song professional handoff.

## Current full-song validation target

The current validation target is:

```text
local audio file
-> structural profile
-> professional terminology report
-> online AI handoff
```

Validation should check:

```text
1. script chain runs from input to handoff
2. generated profile has segment-level evidence
3. professional terminology layer does not expose machine terms as the main language
4. online handoff contains professional terms and accessible examples in one Markdown file
5. generated output remains local and untracked
```

## Public sample rule

Use public sample pools for reproducible tests.

Do not commit:

```text
copyrighted commercial songs
local music-library files
scraped comments
generated song-specific outputs
```

Public validation samples are for testing the pipeline, not for training taste or writing universal review templates.

## Clean sample criteria

A clean test sample should have:

```text
clear local file provenance
reasonable duration for the tested path
no private user material
no copied comment corpus
no generated output committed back to the repo
```

## Baseline replay status

A previous main replay passed with synthetic / reference-probe material and confirmed the structural-only boundary at that time.

Historical boundary from that replay:

```text
no final listening report
no human calibration
no music review
no genre judgment
no instrument or performer identity claim
no lyric or transcription path
no music generation
```

The current path has moved from structural-only toward professional terminology handoff, but the same validation discipline remains: generated song artifacts are local outputs unless explicitly curated.

## What not to revive

Do not revive early validation docs as current instructions. The old baseline-feature-vs-mapping-packet comparison is useful history, not the current user entry path.
