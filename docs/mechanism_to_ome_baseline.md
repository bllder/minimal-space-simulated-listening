# Mechanism-to-OME Baseline

Status: first minimal mapping layer after `audio_evidence_packet.json`.

This layer translates external audio mechanism evidence into auditable MSSL candidate fields:

```text
audio_evidence_packet.json
→ mechanism-to-OME baseline mapping
→ ome_mapping_packet.json
```

It does **not** produce a listening report.
It does **not** confirm auditory object identity.
It does **not** decide genre, mood, taste, or musical value.
It does **not** prove physical 3D location.

Its only job is to make the first O/M/E candidate bridge explicit.

---

## Script

```text
scripts/run_mechanism_to_ome_baseline.py
```

Default input:

```text
outputs/<input-stem>/audio_evidence_packet.json
```

Default output:

```text
outputs/<input-stem>/ome_mapping_packet.json
```

Both files are generated local material and should stay ignored by git.

---

## Run

After generating an evidence packet with the librosa baseline adapter:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mechanism_to_ome_baseline.py `
  --input "outputs\<input-stem>\audio_evidence_packet.json"
```

Optional explicit output path:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mechanism_to_ome_baseline.py `
  --input "outputs\<input-stem>\audio_evidence_packet.json" `
  --output "outputs\<input-stem>\ome_mapping_packet.json"
```

This script uses only the Python standard library.

---

## Output groups

The output packet contains:

```text
O_space
M_domain
E_space
object_candidate_inputs
mapping_rule_index
audit
```

These are still candidates, not final claims.

---

## Baseline mapping rules

### 1. RMS / RMS delta → pressure and continuity candidates

Source evidence:

```text
features.temporal_evidence.rms
features.temporal_evidence.rms_delta
```

Target fields:

```text
M-domain.pressure_transfer_candidate
M-domain.activity_continuity_candidate
E-space.receiver_side_perceived_pressure_candidate
```

Can support:

```text
energy activity
pressure-transfer candidate
sustained vs interrupted activity candidate
```

Cannot prove:

```text
physical distance
near-field truth
emotional intensity
final perceived loudness
```

---

### 2. Spectral centroid / rolloff / bandwidth / flatness → brightness and density candidates

Source evidence:

```text
features.spectral_evidence.spectral_centroid_hz
features.spectral_evidence.spectral_rolloff_hz
features.spectral_evidence.spectral_bandwidth_hz
features.spectral_evidence.spectral_flatness
```

Target fields:

```text
O-space.source_side_spectral_brightness_candidate
O-space.source_side_spectral_density_candidate
E-space.receiver_side_upper_tendency_candidate
object-candidate-input.texture_mass_input
```

Can support:

```text
upper-frequency tendency
broad-band texture candidate
brightness / density evidence before report language
```

Cannot prove:

```text
instrument identity
mood
real source location
visual height
report wording such as bright, cold, sharp, beautiful
```

---

### 3. Side-to-mid / L-R balance / phase correlation → receiver-side spatial proxy candidates

Source evidence:

```text
features.stereo_proxy_evidence.side_to_mid_ratio
features.stereo_proxy_evidence.lr_balance_negative_left_positive_right
features.stereo_proxy_evidence.phase_correlation_proxy
```

Target fields:

```text
E-space.receiver_side_width_candidate
E-space.receiver_side_lr_balance_candidate
E-space.receiver_side_spread_candidate
```

Can support:

```text
receiver-side width candidate
left-right balance candidate
spread / diffusion candidate
spatial continuity input across windows
```

Cannot prove:

```text
real physical 3D source location
room geometry
speaker placement
HRTF
surround field
```

---

### 4. Onset strength / beat evidence → pulse and rhythmic object inputs

Source evidence:

```text
features.rhythm_evidence.onset_strength
features.rhythm_evidence.beat_count
features.rhythm_evidence.beat_track_tempo_bpm
```

Target fields:

```text
M-domain.pulse_transfer_candidate
object-candidate-input.rhythmic_object_input
object-candidate-input.transient_activity_input
```

Can support:

```text
pulse candidate
repeated impact candidate
transient event candidate
object recurrence input
```

Cannot prove:

```text
meter truth
drum identity
kick / snare / percussion identity
groove quality
performance quality
```

---

### 5. Chroma / mel / MFCC → harmonic and timbre-shape candidates

Source evidence:

```text
features.harmonic_evidence.chroma_by_pitch_class
features.harmonic_evidence.dominant_pitch_class_candidate
features.mel_mfcc_evidence.mel_band_db_stats
features.mel_mfcc_evidence.mfcc_stats
```

Target fields:

```text
O-space.source_side_harmonic_contour_candidate
O-space.source_side_timbre_shape_candidate
object-candidate-input.harmonic_layer_input
object-candidate-input.texture_mass_input
```

Can support:

```text
harmonic persistence candidate
timbre-envelope candidate
coarse contour or texture-shape comparison across windows
```

Cannot prove:

```text
key truth
melody truth
chord truth
instrument identity
singer identity
speaker identity
emotion
```

---

## Candidate packet discipline

Every candidate must include:

```text
field
layer
value
confidence
source_features
can_support
cannot_prove
```

This prevents audio mechanism outputs from becoming direct report language.

---

## Why this layer exists

The librosa adapter produces feature evidence.

This layer answers:

```text
Which O/M/E candidate field can this evidence support?
What can the evidence not prove?
How confident is the candidate based on feature availability?
```

It does not answer:

```text
What is the final auditory object?
What does the song mean?
What should the report say?
What should a human hear?
```

Those require later layers:

```text
object candidate building
→ temporal-spatial object tracking
→ auditory scene graph
→ human annotation / calibration
→ listening report
```

---

## Next step

The next layer should be:

```text
object-candidate-baseline
```

It should read `ome_mapping_packet.json` and produce object candidates with:

```text
object_id
candidate_type
supporting_OME_fields
time_window
spatial_proxy_state
continuity_inputs
relation_inputs
cannot_prove
```

Still no final listening report yet.
