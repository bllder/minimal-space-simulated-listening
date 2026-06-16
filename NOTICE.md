# Notice

This repository contains the current clean rebuild of **Minimal Space for Simulated Listening**.

## Project material

Project-authored source code is covered by the source-code license in `LICENSE.md`.

Project-authored documentation, diagrams, notes, README text, and conceptual writing are covered by the documentation/media license in `LICENSE.md`, unless a specific file says otherwise.

## Third-party references

Scientific papers, articles, documentation pages, encyclopedic references, datasets, libraries, and tool names mentioned in this repository remain the property of their respective authors and publishers.

They are used as references only. Their citation in this repository does not mean they are copied, redistributed, relicensed, or endorsed by the project.

## Reference handling rule

Do not commit full third-party PDFs, copyrighted audio, raw music files, scraped comments, large generated outputs, or local analysis artifacts into this repository unless there is a clear legal right and project reason to do so.

Preferred handling:

```text
third-party source
→ cite metadata / DOI / URL / title
→ summarize relevance
→ record safe and unsafe interpretation boundaries
```

## Audio and media boundary

This project should not store copyrighted songs, commercial audio, user-local music libraries, or generated analysis outputs in Git history.

Use local folders ignored by `.gitignore`, such as:

```text
data/
outputs/
configs/
```

## Name boundary

The names **Minimal Space for Simulated Listening**, **MSSL**, **Groove Ear**, and **给 AI 耳朵** identify this project. Reuse of the code or documents does not imply permission to present another project as the official continuation of this one.
