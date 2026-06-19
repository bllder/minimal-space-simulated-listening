# Original Song Listening Experience Prompt

Status: manual external LLM protocol. This is not a renderer and not part of the default MSSL pipeline.

Use this protocol only after the user explicitly asks for original-song listening-experience language.

The input should be an evidence pack generated from existing MSSL outputs.

```text
MSSL structural evidence
+ listening_experience_evidence_pack.json
-> bounded listening-experience language
```

## Claim layers

The response may use these layers only when the pack contains supporting evidence:

```text
source-family hypothesis
melody or pitch-contour proxy
vocal-object hypothesis
style-behavior hypothesis
affective-listening tendency
```

## Claim discipline

Do not treat any layer as truth.

```text
source-family hypothesis != instrument truth
melody proxy != full transcription
vocal-object hypothesis != real-world identity
style-behavior hypothesis != genre truth
affective-listening tendency != emotion truth
```

## Output shape

Do not use a fixed template. Let the evidence decide whether the response should be a whole-song sketch, a segment reading, or an object-centered reading.

Every strong sentence should be traceable to a segment, claim layer, support value, or evidence field in the pack.

When evidence is weak, say it is weak. When evidence is missing, do not fill the gap.

## Red lines

Do not output ratings, taste judgment, marketing language, unsupported category labels, unsupported lyric interpretation, or raw MSSL field names as human-facing prose.
