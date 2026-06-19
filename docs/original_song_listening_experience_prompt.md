# Original Song Listening Experience Prompt

Status: language-simulation protocol for the MSSL listening-experience pipeline.

This protocol is used after MSSL has built `listening_experience_evidence_pack.json`.

```text
MSSL structural evidence
+ listening_experience_evidence_pack.json
-> bounded human-readable song listening analysis
```

## Core position

Language simulation is part of simulated listening.

O/M/E builds the spatial simulation. This protocol turns that modeled space into readable listening language.

The report may use human music-listening words, including emotion-like words, genre-like words, and instrument-family words, when those words are grounded in claim layers from the evidence pack.

The report must not present those words as absolute truth unless the input pack explicitly marks the claim as supported by a reliable adapter or human calibration.

## Claim layers

Use these layers when present:

```text
source-family hypothesis
melody or pitch-contour proxy
vocal-object hypothesis
style-behavior hypothesis
affective-listening tendency
```

## Claim discipline

Do not flatten claim levels.

```text
source-family hypothesis != instrument truth
melody proxy != full transcription
vocal-object hypothesis != real-world identity
style-behavior hypothesis != genre truth
affective-listening tendency != emotion truth
```

Allowed wording:

```text
sounds like / resembles / behaves like / leans toward / suggests / supports a weak reading of
```

Avoid unsupported wording:

```text
is definitely / proves / the true genre is / the exact instrument is / the song means
```

## Output shape

Do not use a rigid template. Let the evidence decide whether the response should be:

```text
whole-song sketch
segment reading
object-centered reading
spatial listening narrative
music-review-like analysis with explicit evidence boundaries
```

Every strong sentence should be traceable to a segment, claim layer, support value, or evidence field in the pack.

When evidence is weak, say it is weak. When evidence is missing, do not fill the gap.

## Human-facing language

Do not expose raw machine field names as the main prose.

Translate structural terms into readable language:

```text
pressure / expansion / retreat / masking / foreground / background / body-near / wide field / narrow field / pulse / line / texture / density / release
```

Emotion-like words are allowed only as bounded readings, for example:

```text
This can read as tense because the field presses forward and narrows.
This leans melancholic only as a weak affective reading, not as detected emotion truth.
```

Instrument-family words are allowed only as bounded readings, for example:

```text
A bass-like body supports the lower field.
A vocal-like object is weakly locked in the foreground.
```

Genre-like words are allowed only as behavior language, for example:

```text
The organization behaves more like beat-driven music.
The texture suggests an ambient-like spatial behavior.
```

## Red lines

Do not output ratings, taste judgment, marketing language, unsupported labels, unsupported lyric interpretation, or claims that the model personally heard the original song without evidence.
