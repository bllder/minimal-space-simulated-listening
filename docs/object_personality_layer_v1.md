# Object Personality Layer v1

Status: experimental / optional. This is not part of the default main handoff path.

## Purpose

Convert detected audio objects into behavioral agents in a listening field.

This layer may be useful for experiments, but it must not replace aesthetic context, MIR/context adapters, user listening language, or external close-listening material.

---

## Core Definition

An object is defined as:

- a persistent perceptual entity
- with temporal behavior
- interacting with other objects in a listening field

---

## Object Schema (v1)

```json
{
  "object_id": "string",
  "name": "string",
  "behavior": ["verb-like perceptual actions"],
  "motion_style": "string",
  "spatial_role": "foreground | background | field | transient",
  "interaction": ["relations to other objects"],
  "stability": "stable | semi-stable | volatile",
  "affective_signature": "string (non-emotion label, descriptive only)"
}
```

---

## Behavior Vocabulary (initial)

- expands
- compresses
- drifts
- anchors
- dissolves
- emerges
- recedes
- overlays
- fragments
- stabilizes

---

## Rules

1. Do not output genre or emotion as primary label.
2. Behavior > identity.
3. Interaction > isolation.
4. Objects must persist across time windows when possible.
5. Do not let this layer become a substitute for human/aesthetic context.

---

## Optional Position

```text
structural evidence
→ O/M/E mapping
→ listening-experience evidence pack
→ critical listening brief
→ aesthetic context handoff
→ online AI handoff
```

Experimental branch of the runtime only:

```text
--experimental-object-personality
```

---

## Non-goals

- no music theory explanation
- no genre classification system
- no recommendation system
- no sentiment scoring system
- no replacement for aesthetic context handoff
