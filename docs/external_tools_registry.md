# External Tools Registry for MSSL V4.1

MSSL should not reimplement every existing MIR / audio-AI layer. Existing tools may be used as evidence adapters. They are references and optional adapters, not the conceptual core of the project.

MSSL core remains:

```text
common audio / music evidence
+ optional external adapter evidence
-> MSSL O/M/E translation
-> listening-space report
```

## P0. Music structure segmentation

Default V4.1 runtime uses a lightweight full-mix novelty detector and snaps boundaries toward the bar-like grid when possible.

Optional references:

- MSAF / Music Structure Analysis Framework: Python framework for music structure analysis. GitHub: https://github.com/urinieto/msaf
- librosa: Python library for audio and music analysis; useful for feature extraction and self-similarity / recurrence-based experiments. GitHub: https://github.com/librosa/librosa
- LinkSeg: music structure analysis via pairwise link prediction and graph attention, useful as a future research reference for structure labels. GitHub: https://github.com/morgan76/LinkSeg
- All-In-One Music Structure Analyzer: predicts tempo, beats, downbeats, functional segment boundaries, and labels. GitHub: https://github.com/mir-aidj/all-in-one
- madmom: MIR-oriented Python audio signal processing library, useful for beat/downbeat experiments. GitHub: https://github.com/CPJKU/madmom

MSSL rule:

```text
External tool output -> structure candidate evidence
MSSL output -> intro-like / verse-like / chorus-like / bridge-like / outro-like listening structure
```

Do not present the labels as final musicological truth.

## P1. MIDI-like symbolic reduction

Default V4.1 runtime provides only a heuristic MIDI-like skeleton from full-mix evidence.

Optional references:

- Basic Pitch: Spotify audio-to-MIDI / automatic music transcription library. GitHub: https://github.com/spotify/basic-pitch
- Omnizart: automatic music transcription toolkit for pitched instruments, vocal melody, chords, drum events, and beat. GitHub: https://github.com/Music-and-Culture-Technology-Lab/omnizart
- MT3: multi-task multitrack music transcription model. GitHub: https://github.com/magenta/mt3

MSSL rule:

```text
Do not output full scores as fact.
Extract a simplified skeleton:
- melody contour
- bass motion
- harmony block
- phrase shape
- note density
```

## P2. Source separation / instrument evidence

Default V4.1 runtime does not run source separation. It only produces source hypotheses from the full stereo mix.

Optional references:

- python-audio-separator / Audio Separator: CLI / Python package for separating audio into stems, using MDX-Net, VR, Demucs, MDXC models from the UVR ecosystem. GitHub: https://github.com/nomadkaraoke/python-audio-separator
- Demucs: source separation baseline for vocals / drums / bass / other, with HTDemucs and experimental finer stems. GitHub: https://github.com/facebookresearch/demucs
- Ultimate Vocal Remover GUI: broader UVR ecosystem reference. GitHub: https://github.com/Anjok07/ultimatevocalremovergui

MSSL rule:

```text
stem != object
stem -> source evidence for object candidate
```

Example:

```text
object_03_harmonic_layer
  source_evidence:
    other_stem: high
    piano/synth candidate: medium
    vocal leakage: possible
```

## P3. Vocal transcription / lyric alignment

Default V4.1 runtime does not transcribe lyrics. It only records vocal-contour candidates and lyric-alignment status.

Optional references:

- Qwen3-ASR: multilingual ASR family with timestamp / forced-alignment direction. GitHub: https://github.com/QwenLM/Qwen3-ASR
- FunASR: speech recognition toolkit with multilingual support and streaming / diarization directions. GitHub: https://github.com/modelscope/FunASR
- WhisperX: ASR with word-level timestamps and forced alignment. GitHub: https://github.com/m-bain/whisperX

MSSL rule:

```text
vocals stem or mix
-> ASR / alignment
-> lyric phrase timestamps
-> MSSL vocal object
```

No singer identity, no voiceprint recognition, no public dumping of full copyrighted lyrics in project reports.

## P4. Listening language layer

No external project should replace this. It is a MSSL-owned layer.

The layer translates machine evidence into human-readable listening notes while preserving uncertainty.

## P5. MSSL spatial narrative

No external project should replace this either. Existing tools provide evidence; MSSL translates evidence into O/M/E listening-space structure.
