# Librosa Baseline Evidence

Status: first executable baseline evidence adapter.

This layer turns a local audio file into a machine-readable evidence packet.
It does **not** produce an MSSL listening report.
It does **not** decide genre, mood, taste, or musical value.
It does **not** perform source separation, singer identification, ASR, lyric recognition, or physical 3D localization.

Its only job is:

```text
audio file
→ librosa feature evidence
→ audio_evidence_packet.json
→ later mechanism-to-OME translation
```

---

## Script

```text
scripts/run_librosa_baseline_evidence.py
```

Default output:

```text
outputs/<input-stem>/audio_evidence_packet.json
```

The output folder is generated local material and should stay ignored by git.

---

## Install dependency locally

Use the project venv Python only.

Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install librosa
```

macOS / Linux:

```bash
./.venv/bin/python -m pip install librosa
```

Do not use global `pip`, `python`, or `python3`.

---

## Run

Windows example, from the project root:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_librosa_baseline_evidence.py `
  --input "path\to\local_audio.wav" `
  --output-dir outputs
```

macOS / Linux example, from the project root:

```bash
./.venv/bin/python ./scripts/run_librosa_baseline_evidence.py \
  --input "path/to/local_audio.wav" \
  --output-dir outputs
```

Optional windowed run on Windows:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_librosa_baseline_evidence.py `
  --input "path\to\local_audio.wav" `
  --window-start 42 `
  --window-duration 8 `
  --output-dir outputs
```

Optional windowed run on macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_librosa_baseline_evidence.py \
  --input "path/to/local_audio.wav" \
  --window-start 42 \
  --window-duration 8 \
  --output-dir outputs
```

---

## Evidence groups

The script produces these groups:

```text
temporal_evidence
spectral_evidence
rhythm_evidence
harmonic_evidence
mel_mfcc_evidence
stereo_proxy_evidence
```

### temporal_evidence

Fields include:

```text
RMS
zero-crossing rate
RMS delta
downsampled RMS timeline preview
```

MSSL use:

```text
time activity
energy change
possible pressure-transfer evidence
continuity / discontinuity cue
```

Cannot prove:

```text
emotion
genre
near-field position by itself
object identity
```

### spectral_evidence

Fields include:

```text
spectral centroid
spectral bandwidth
spectral rolloff
spectral flatness
spectral contrast
```

MSSL use:

```text
brightness / darkness candidate
spectral density candidate
band-shift evidence
texture contrast evidence
```

Cannot prove:

```text
physical source location
instrument identity by itself
listening report language
```

### rhythm_evidence

Fields include:

```text
onset strength
tempo estimate
beat-track tempo
beat time preview
onset timeline preview
```

MSSL use:

```text
pulse candidate
onset-object candidate
rhythmic activity evidence
```

Cannot prove:

```text
musical structure truth
meter truth
groove quality score
```

### harmonic_evidence

Fields include:

```text
chroma statistics
dominant pitch-class candidate
```

MSSL use:

```text
harmonic-contour evidence
pitch-class distribution candidate
repetition / persistence support
```

Cannot prove:

```text
key truth
melody truth
song meaning
```

### mel_mfcc_evidence

Fields include:

```text
mel-band dB statistics
MFCC statistics
```

MSSL use:

```text
timbre-shape evidence
texture / spectral envelope support
mechanism-to-OME input
```

Cannot prove:

```text
speaker identity
singer identity
emotion
music review wording
```

### stereo_proxy_evidence

Fields include:

```text
left RMS
right RMS
left-right balance
mid RMS
side RMS
side-to-mid ratio
phase-correlation proxy
```

MSSL use:

```text
receiver-side width candidate
left-right balance candidate
center-side relation candidate
spread / diffusion candidate
```

Cannot prove:

```text
real physical 3D source position
room geometry
speaker placement
HRTF
```

---

## Output boundary

This packet is allowed to say:

```text
RMS increased
onset density is high
side-to-mid ratio is high
spectral centroid shifted upward
chroma distribution changed
```

It is not allowed to say:

```text
this song is beautiful
this song is sad
this is the final listening center
this object is definitely a vocal
this sound is physically located here
```

Those interpretations require later MSSL layers.

---

## Next step

The next layer should be:

```text
mechanism-to-OME baseline
```

It should map evidence into fields such as:

```text
RMS / loudness → perceived_pressure candidate
spectral centroid → brightness / upper tendency candidate
side-to-mid ratio → width / spread candidate
onset strength → rhythmic object probability
chroma / MFCC / mel stats → contour or texture candidate
```

Every mapping rule must include:

```text
can_support
cannot_prove
OME_target_field
confidence
```
