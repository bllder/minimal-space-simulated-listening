# C. Online Handoff and Translation

Status: consolidated online-AI handoff, translation style, and external-context alignment guide.

Use this file as the default prompt protocol source for `scripts/run_listening_experience_pipeline.py` and as the policy source for `translation_style_guidance` in `scripts/build_listening_experience_prompt.py`.

Consolidated from:

- `original_song_listening_experience_prompt.md`
- `aesthetic_context_handoff.md`
- `comment_corpus_audit_notes_v0.md`
- `user_ear_seed_cases_v0.md`

## Current local responsibility

MSSL locally produces:

```text
professional audio descriptors
timeline anchors
object / layer hypotheses
translation examples
external-context alignment slots
```

MSSL locally does not produce:

```text
final review content
lyrics
external reviews
artist background text
song meaning truth
genre truth
emotion truth
```

The online AI may use its own available context and rules. MSSL only gives professional anchors and timeline structure.

## Core handoff axis

```text
MSSL professional audio report
+ online AI's own external context if available
-> timeline-grounded accessible listening analysis
```

External context should be aligned to the MSSL timeline. It should not replace the local audio descriptors.

## Claim layers

When present, treat these as bounded layers:

```text
source-family hypothesis
melody or pitch-contour proxy
vocal-object hypothesis
style-behavior hypothesis
affective-listening tendency
external song context
public comment or review context
user aesthetic seed
```

## Claim discipline

```text
source-family hypothesis != instrument truth
melody proxy != full transcription
vocal-object hypothesis != singer identity
style-behavior hypothesis != genre truth
affective-listening tendency != emotion truth
lyrics / reviews / comments != MSSL audio proof
```

Allowed wording:

```text
sounds like / resembles / behaves like / leans toward / suggests / supports a weak reading of
```

Avoid unsupported wording:

```text
is definitely / proves / the true genre is / the exact instrument is / the song means
```

## Translation style guidance

The online AI should translate professional descriptors into accessible language only when useful.

Preferred movement:

```text
professional descriptor
-> perceptible language
-> time range
-> relation to foreground / background / space / rhythm / texture
```

Do not turn the final review into an engineering checklist.

## Accessible translation examples

These are style examples, not mandatory wording.

| Professional anchor | Possible accessible translation direction |
|---|---|
| low apparent source width | the sound image stays concentrated rather than spreading sideways |
| high listener envelopment | the field begins to wrap around the listener |
| reduced transient energy | attacks feel softened or less percussive |
| pronounced rhythmic articulation | the pulse becomes easier to follow physically |
| low-frequency foundation | the bottom of the mix gives weight or ground support |
| foreground lead-line candidate | a traceable front line leads the segment without proving singer or instrument identity |
| diffuse texture masking | edges blur or a texture bed softens object boundaries |
| harmonic spatial widening | the support layer opens the field around the foreground |

## External context alignment

If external context is available to the online AI, align it to the local report through these targets:

```text
time range
professional spatial terms
foreground lead-line / source-family hypotheses
texture and layering
dynamics and motion
timbre and low-frequency foundation
section or movement function
```

MSSL does not supply or police the external context itself. The online AI handles its own search, platform rules, and final output behavior.

## Aesthetic context role

Use MSSL as:

```text
structural constraint
evidence organizer
boundary checker
professional audio anchor
```

Use aesthetic / external context as:

```text
human listening entry
vocabulary source
cultural and memory context
criticism orientation
```

Do not let MSSL act as the only mouth of the report.

## Context classification before interpretation

Before interpreting an external name, note, playlist title, or uploaded text, classify it lightly:

```text
private naming
style cluster
label entry
single-work research
test / probe set
memory anchor
external metadata
unknown
```

Do not poetically expand context before classification. Yes, this rule exists because machines keep trying to make every filename into a prophecy.

## Comment and user-ear use

Comments are not evidence of what the song is. They are evidence of how humans may enter the song.

A useful comment or review pattern must reconnect to the song's listening field through at least one of:

```text
sound
body
scene
time
memory
lyric meaning
public use
performance
production
cultural context
```

Use comment-derived material only as possible human-language entry points after paraphrase and filtering.

## User-ear diagnostic habit

For any new song:

```text
Listen to the song first.
Then ask whether a comment or phrase actually connects back to that song.
Transfer the question, not the answer.
```

Reusable diagnostic questions:

```text
Where does the language enter the song?
What does it connect to: lyric, sound, body, scene, memory, culture, or public use?
What can it support: structure, context, reception, or translation style?
Does it detach into platform noise, fandom, generic emotion, private story, or meme?
```

## Online AI output request pattern

Use this shape when the user asks the online AI to write:

```text
Read the professional audio report and timeline.
Use the professional terms as anchors, not as mandatory wording.
If external context is available to you, align it to the timeline.
Write a time-grounded, space-grounded close-listening review in accessible language.
Do not replace the local audio descriptors with generic background or mood claims.
```

## Red lines for local MSSL handoff

The local handoff should not include:

```text
ratings
taste judgment
marketing language
unsupported labels
unsupported lyric interpretation
claims that MSSL personally heard the song
raw long comments or copied review bodies
```
