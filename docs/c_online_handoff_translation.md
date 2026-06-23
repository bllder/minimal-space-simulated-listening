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

The online AI may use its own available context and rules. MSSL gives professional anchors, timeline structure, and a report-facing task frame.

## Core handoff axis

```text
MSSL professional audio report
+ online AI's own external context if available
-> timeline-grounded accessible listening analysis
```

External context should be aligned to the MSSL timeline. It should not replace the local audio descriptors.

## Online-AI report presentation

The uploadable online-AI handoff should be presented as three distinct parts:

```text
1. review-direction prompt
2. professional audio evidence / numeric-to-term translation
3. review writing style guidance / public-review examples
```

These parts must not be merged into one undifferentiated prompt. Each part has a different job.

### Part 1 — Review-direction prompt

This part tells the online AI what to do with the handoff.

Required content:

```text
You have not received the audio file.
You are receiving local MSSL listening evidence.
First, try to verify the song identity using filename or user-supplied clues, duration, MSSL style candidates, and your own search results.
If identity is reasonably confirmed, search lyrics, album / artist / release background, public reviews, reception notes, and relevant comments.
If identity is uncertain, do not invent lyrics, background, exact song meaning, or public reception.
Write a Chinese close-listening review by combining MSSL audio evidence with verified external context.
```

Important boundary:

```text
MSSL evidence can help constrain identity and style hypotheses, but it is not an audio fingerprint.
Do not claim the numbers alone identify a song.
```

The online AI may use search, but its search results must be treated as an external context layer, not as local MSSL audio proof.

### Part 2 — Professional audio evidence / numeric-to-term translation

This part is the local MSSL evidence layer.

It should use the already built numeric-to-professional-term translation path:

```text
machine field / numeric proxy
-> mechanism evidence term
-> qualitative professional band
-> professional report descriptor
-> human listening affordance
```

Raw numbers may remain available for traceability, but they should not be the main prose surface of the handoff. The online AI should see professional descriptors first, then use hidden or secondary numeric evidence only for self-checking.

Preferred presentation:

```text
Spatial field:
- center-concentrated / laterally open / diffuse / enveloping tendency
- boundary: not physical room width or exact source location

Pressure and intensity:
- restrained / moderate / rising / held / released perceived pressure proxy
- boundary: not true listener emotion or calibrated SPL

Low-frequency foundation:
- light / stable / thickening / grounding low-end support
- boundary: not bass-instrument truth

Foreground and source-family candidates:
- vocal-like foreground stream candidate
- percussive pulse layer candidate
- harmonic support layer candidate
- boundary: not singer, lyric, or exact instrument identity

Texture and motion:
- blurred edges / dense masking load / pulsing / drifting / forward pressure
- boundary: not production intention truth
```

Avoid report prose like:

```text
pressure = 0.42
width = 0.0001
motion = 0.34
```

Prefer report prose like:

```text
The field stays tightly centered and does not open much to the sides.
The low-frequency foundation remains present and grows more weight-bearing toward the later section.
The foreground stream remains trackable, but it should be described as vocal-like or lead-line-like unless external context confirms identity.
```

### Part 3 — Review writing style guidance / public-review examples

This part gives the online AI a human writing target.

The goal is not to copy public reviews, comments, or seed cases. The goal is to show how human music criticism often combines:

```text
arrangement / instrumentation family
sound field / atmosphere
lyric theme
album, artist, release, or production context
cover / visual / cultural context when relevant
public reception and comments
body, scene, memory, and time
```

Useful public-review-style patterns:

```text
A track description may combine guitar-like harmonic material, soft chordal support, reduced percussive impact, instrumental whitespace, lyric solitude, and private atmosphere.
A song review may connect mid-tempo melodic narration, low-frequency support, arrangement movement, core lyric metaphor, and album-wide imagery.
An album review may connect musical transformation, character identity, cover design, public genre position, and the artist's career movement.
```

Use this as style guidance, not a source of facts for the target song.

Diagnostic guard:

```text
Do not assume:
青春流行 = 初恋主题
舞曲 = 快乐主题
低频重 = 愤怒主题
空间大 = 宏大主题
评论多 = 歌曲真义
```

Instead ask:

```text
What do the verified lyrics, arrangement, sound field, public context, and MSSL evidence actually support?
Is the song about first love, memory, distance, public nostalgia, bodily release, resistance, solitude, or something else?
What concrete sensory objects, body actions, scenes, or public uses let the review language enter this song?
```

The transferable unit is the diagnostic question, not the seed-case answer.

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
-> verified lyric / background / review context when available
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
lyrics and lyric images if identity is confirmed
album / artist / release background if identity is confirmed
public reviews and reception if identity is confirmed
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
First verify the song identity if possible through filename / user clues, duration, MSSL style candidates, and public search.
If identity is confirmed, search lyrics, album / artist / release background, public reviews, reception notes, and comments.
If identity is uncertain, do not invent external context.
Write a time-grounded, space-grounded close-listening review in accessible Chinese.
Do not replace the local audio descriptors with generic background or mood claims.
Do not directly quote raw numeric values in the final review unless the user explicitly asks for technical evidence.
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
