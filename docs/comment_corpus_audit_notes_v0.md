# Comment Corpus Audit Notes v0

Status: external-corpus audit notes for MSSL listening-language work.  
Source status: based on a Kimi-produced audit report over user-provided NetEase / Douban comment and review files.  
Scope: data quality, label-noise diagnosis, usable evidence boundaries, and MSSL reuse rules.  
Non-scope: this is not a music review, not a label schema, not a gold-standard dataset, and not raw comment storage.

## Why this task was done

The original task was not to ask Kimi to interpret music. Kimi was used as a low-cost external worker for corpus inspection:

```text
Read the uploaded comment/review files.
Check whether the inputs are real and complete.
Find duplicate, missing-field, and short-text problems.
Audit old labels for obvious contamination.
Estimate which kinds of human listening-language anchors appear in the corpus.
Produce candidate examples for later human review.
```

The goal was to support the MSSL listening-translation layer:

```text
MSSL structural / machine-listening output
+ audio-analysis dimensions
+ lyrics / professional review / context search
+ MIR / tag-library weak evidence
+ human-comment language material
+ user-ear calibration
= bounded human listening-language synthesis
```

Kimi is not the judge. It is a crawler / rough auditor / weak relabeler. Its output can expose data problems and candidate patterns, but it must not define MSSL theory or final listening judgments.

## What this audit was meant to obtain

The useful target was not `good music criticism`. The useful target was an error map:

1. Whether the corpus was readable and actually based on the supplied files.
2. Whether old anchor labels were contaminated by shallow keyword rules.
3. Whether sound-specific anchors dominate, or whether human listening comments more often enter through memory, relationship, scene, body, emotion, or judgment.
4. Which comment types are useful as report-language hints, and which are platform / fandom / meme / private-story noise.
5. Whether the MSSL criterion should remain `can reconstruct sound`, or expand to `can reconstruct a listening field`.

## Data status reported by the audit

The Kimi report declared:

```text
DATA_SOURCE_STATUS = real_input
```

Reported corpus sketch:

- NetEase comments: 6,897 rows.
- NetEase usable after dedupe: about 5,404 rows.
- NetEase duplicate rate: about 21.6%.
- NetEase coverage: 24 songs.
- NetEase metadata issue: album field reported as 100% missing.
- Douban reviews: 646 rows, 637 unique.
- Douban review shape: 100% short comments; median length about 15 characters.
- Douban long-review limitation: only 5 items above 200 characters.

These figures are useful for corpus planning, not for musical interpretation.

## Major old-label contamination patterns

The report flagged severe old-label problems:

| Old label | Reported problem | MSSL interpretation |
|---|---|---|
| `lyric_anchor` | Nearly any occurrence of a singer / song-name keyword could trigger it | This label cannot be trusted without checking actual lyric discussion |
| `sound_anchor` | Generic `good song`, `heard before`, or vague praise was often treated as sound evidence | Sound evidence must describe timbre, vocal, rhythm, arrangement, mix, spatial feel, or musical motion |
| `body_anchor` | Narrative crying / sadness was often treated as bodily listening | Body evidence should describe embodied response, movement, pressure, breath, tears, dancing, bodily memory, or physical listening position |
| `listener_position` | First-person pronouns were overread as listening position | `I think` is not enough; the comment must locate a listener in time, place, body, relation, or use context |

These are not final statistics. They are a warning that shallow keyword labels should not be reused.

## Directional findings that can be used

The following findings are useful as direction, not as hard truth:

- Old labels should not be used directly.
- `sound_anchor` is not the dominant form of human music-comment language.
- Many human comments enter songs through memory, relationship, scene, body, emotion, social identity, public use, or aesthetic judgment.
- Therefore the old `can be internally heard as sound` criterion is too narrow.
- A better criterion is:

```text
A useful listening-language unit must help reconstruct a listening field.
The field may include sound, body, scene, time, memory, lyric meaning, social use, performance, production, or cultural context.
```

## What can be used from Kimi output

Use:

- corpus scale and field-quality notes;
- duplicate and short-text warnings;
- old-label error patterns;
- candidate anchor families from `label_schema_v2`;
- broad finding that memory / relationship / scene / body / judgment anchors matter;
- recommendations that align with MSSL's `reproducible listening field` rule;
- candidate examples only after paraphrase, filtering, and user-ear review.

Use with caution:

- relabeled samples;
- platform-level percentages;
- anchor-frequency statistics;
- example lists;
- research-source lists marked unverified.

Do not use:

- raw comment examples as repository content;
- Kimi relabels as gold labels;
- Kimi music interpretation as final analysis;
- raw NetEase / Douban rows in GitHub;
- platform comments as song truth;
- unverified research-source claims as citations.

## Why raw examples should not enter the repository

Music comments often contain private memory, timestamps, grief, relationship history, platform identity, and other context that should not be preserved in project documentation. The repository should store only the minimum useful abstraction:

```text
raw comment -> paraphrased pattern -> anchor type -> failure mode -> MSSL use rule
```

Do not store usernames, IDs, like counts, exact timestamps, full personal stories, long lyrics, long reviews, or copied comment bodies.

## Relation to `user_ear_seed_cases_v0.md`

These two documents have different jobs:

```text
docs/comment_corpus_audit_notes_v0.md
= large-sample corpus audit and label-contamination map

docs/user_ear_seed_cases_v0.md
= human-ear seed cases for judging whether language actually connects back to a song
```

Kimi tells MSSL where the corpus is noisy.  
User-ear seed cases tell MSSL how to judge alignment.

Neither document is a report template.

## Reuse protocol for future listening-language analysis

For a new song, do not begin from comment labels. Begin from the song and evidence bundle:

```text
1. Run or collect MSSL machine-listening evidence.
2. Summarize relevant structural packets: object candidates, spatial field, movement, pressure, density, width, persistence, masking, and relations.
3. Add professional audio-analysis dimensions when useful: melody, harmony, rhythm, meter, tempo, vocal performance, arrangement, instrumentation, timbre, dynamics, stereo space, production, mix, section motion, and source relationships.
4. Search for lyrics, professional reviews, interviews, public reception, and cultural context.
5. Use MIR / tag-library evidence as weak priors: genre, mood, activity, tempo, key, chord hints, structure hints, vocal/instrument hints, similarity hints.
6. Use comment corpus patterns only as possible human-language entry points.
7. Use user-ear seed cases to audit whether a comment or phrase actually reconnects to the song.
8. Write a human-facing listening analysis that synthesizes evidence, rather than dumping evidence.
```

## Comment evidence states

When using comment-derived material, classify it lightly:

| State | Meaning | Allowed use |
|---|---|---|
| `usable_context` | The comment reconnects to lyric, sound, body, scene, memory, public use, or performance in a song-specific way | Can inform report-language hints after paraphrase |
| `weak_context` | The comment gives a plausible human response but lacks detail or song-specific coupling | Can guide search / questions, not report claims |
| `meme_noise` | The comment is mostly joke, platform meme, fandom, or old internet time-capsule | Use only if meme has reshaped public listening |
| `private_detached_story` | The story is emotional but not coupled to the song | Do not use as song evidence |
| `platform_noise` | Membership, access, copyright, ranking, app behavior | Do not use as listening evidence |
| `uncertain` | Not enough information | Hold for human review |

## Minimal MSSL rule

```text
Comments are not evidence of what the song is.
Comments are evidence of how humans may enter the song.

A comment is useful only when it reconnects to the song's own listening field.
A label is useful only when it survives song-first review.
A report is useful only when it combines MSSL structure, music evidence, search context, weak MIR priors, and human-ear alignment without collapsing them into a fixed template.
```
