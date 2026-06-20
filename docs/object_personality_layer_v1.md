# Object Personality Layer v1

## Purpose
Convert detected audio objects into behavioral agents in a listening field.

Not classification. Not labels.
Behavior over time.

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

1. Do not output genre or emotion as primary label
2. Behavior > identity
3. Interaction > isolation
4. Objects must persist across time windows when possible

---

## Output Position in Pipeline

structural evidence
→ O/M/E mapping
→ object personality layer  ← HERE
→ critical listening brief
→ LLM criticism

---

## Non-goals

- no music theory explanation
- no genre classification system
- no recommendation system
- no sentiment scoring system
