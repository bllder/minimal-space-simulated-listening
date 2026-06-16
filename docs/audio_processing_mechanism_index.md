# Audio Processing Mechanism Index

Project: **Minimal Space for Simulated Listening**  
Status: mechanism reference layer

---

## 1. Purpose

MSSL does not invent the audio mechanisms used by audio editors, DSP systems, MIR tools, or psychoacoustic models.

MSSL selects existing mechanisms, constrains them, and translates their outputs into O/M/E listening-space evidence.

```text
existing audio mechanism
-> measured evidence
-> MSSL evidence field
-> O/M/E translation
-> listening object support
```

---

## 2. Mechanism table

| Mechanism | Source / theory area | Output | MSSL evidence role | Boundary |
|---|---|---|---|---|
| Waveform / amplitude over time | sampled audio signal | amplitude, RMS, peak, envelope | temporal pressure evidence | Does not alone mean near/far. |
| FFT | Fourier analysis | global or windowed frequency energy | spectral brightness / band evidence | Does not locate sound in space. |
| STFT / spectrogram | windowed Fourier transform | time-frequency local energy | temporal-spectral evidence | Fixed window has time/frequency tradeoff. |
| CWT / wavelet | time-scale analysis | scale-position evidence | multiscale transient vs sustained evidence | Scale is not exact Hz; use pseudo-frequency only. |
| Morlet / Gabor-like wavelet | Gaussian-windowed sinusoid / time-frequency atom | smooth oscillation matching | pitch / contour / burst evidence candidate | Supplement to Fourier, not replacement. |
| Filterbank / ERB-like banding | cochlea-informed psychoacoustics | frequency-selective band energy | biological-auditory constraint | Not a true cochlea simulation. |
| Loudness / dynamics | audio engineering / psychoacoustics | loudness, compression, dynamic range | pressure / masking risk | Not taste or emotion by itself. |
| Stereo mid-side | stereo signal relation | side ratio, width proxy | E-space width / spread evidence | Not true physical room width. |
| Phase correlation | stereo signal relation | correlation / diffusion proxy | center-side / envelopment evidence | Not true 3D localization. |
| Source separation stems | learned music source separation | vocals / drums / bass / other stems | optional object anchor | Stem is not identical to listening object. |
| Vocal activity / F0 / voiced evidence | voice and singing analysis | voicing, pitch contour | optional vocal lock support | Not singer identity, ASR, or lyric recognition. |
| Comb-filter transform | signal / feature transformation | altered feature spectrum | representation-transform reference | Mechanism inspiration only; not an auditory filter claim. |

---

## 3. PDF discussion anchors

The current discussion used these references as mechanism anchors:

```text
DSP: real-time measurement / filtering / compression of analog-derived signals.
CWT: shifted and scaled wavelets create a 2D scale-position view of a 1D signal.
Sadowsky CWT: music needs time-frequency representation because notes happen at times and durations.
Morlet: Gaussian-windowed sinusoid bridge between time and frequency.
Wavelet: correlation with short localized oscillations can identify events in audio.
Cochlea: hearing depends on fluid / membrane motion and sensory conversion.
Auditory filter paper: cochlear tuning and masking are nonlinear and frequency-selective.
Ear recognition comb-filter paper: filters can transform feature vectors without being auditory mechanisms.
Ear-EEG forward model: forward mapping can be useful as a modeling analogy, but MSSL is audio listening, not EEG localization.
```

---

## 4. Naming rule

Prefer:

```text
audio mechanism evidence
mechanism-to-OME translation
```

Avoid:

```text
MSSL invented the filter layer
```

The filter / mechanism layer is an interface layer. O/M/E is the creative representation layer.
