# Baseline Replay Log

## 2026-06-18 main replay

Status: passed.

### Scope

This replay validates the current main baseline after the music understanding summary layer was merged.

This is not a listening report.  
This is not human calibration.  
This does not use copyrighted audio, scraped comments, or local song-specific profiles.

### Commands

```powershell
.\.venv\Scripts\python.exe .\scripts\run_minimal_pipeline_smoke.py --generate-synthetic --output-dir outputs\minimal_pipeline_smoke

.\.venv\Scripts\python.exe .\scripts\run_reference_probe_bank.py

.\.venv\Scripts\python.exe .\scripts\run_music_understanding_summary.py --run-dir outputs\reference_probe_bank\harmonic_layer_plus_pulse\mssl_output

Get-Content outputs\reference_probe_bank\harmonic_layer_plus_pulse\mssl_output\music_understanding_summary.md -Raw -Encoding UTF8

git status --short
```

### Results

- Minimal pipeline smoke: passed.
- Reference probe bank: completed.
- Music understanding summary: generated.
- Git working tree after generated outputs: clean.

### Reference probe summary

For `harmonic_layer_plus_pulse`:

- Window count: 2
- Track count: 6
- Scene node count: 6
- Scene relation count: 26
- Dominant structure: `harmonic_layer_candidate`
- Report boundary: stopped before listening report generation.

### Boundary

The replay confirms that the current pipeline remains structural-only:

- no final listening report
- no human calibration
- no music review
- no genre judgment
- no instrument or singer identity
- no lyrics or ASR
- no music generation

### Notes

Generated files are local outputs and are not intended for Git tracking.
