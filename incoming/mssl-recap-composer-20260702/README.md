# MSSL recap composer patch archive

Uploaded from `归档.zip` on 2026-07-02.

This branch stores the portable patch archive because the uploaded bundle depends on current `main` and cannot be directly applied by the ChatGPT GitHub contents connector.

Base commit verified against current `main`:

```text
ab209a41bedaacd43d586c244109dcefc5a7357b
```

Bundle head:

```text
7fc8b85170c973c98a65f254ea6e7e0bb96bce89 refs/heads/claude/mssl-audio-analysis-plan-iaz4tl
```

To apply locally from this folder after downloading the files:

```bash
git checkout main
git pull --ff-only origin main
git checkout -b claude/mssl-recap-composer

git am incoming/mssl-recap-composer-20260702/0001Wiresourceobjectsandheardlyricfragmentsintod.patch
git am incoming/mssl-recap-composer-20260702/0002Rebuildcompacthandoffintolisteningrecapcompose.patch
git am incoming/mssl-recap-composer-20260702/0003Aligndocswithlisteningrecapcomposerruntime.patch
```

The original archive also contained macOS `__MACOSX` metadata, intentionally not uploaded.
