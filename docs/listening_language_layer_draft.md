# P4 Listening Language Layer Draft

Status: V4.2 human-calibrated layer.

This layer translates machine audio evidence into listener-facing language after the foundation layers have already produced:

```text
whole-song evidence
music-like structure
MIDI-like skeleton proxy
source / instrument evidence proxy
lyric-alignment boundary
MSSL O/M/E spatial evidence
```

P4 does not overwrite the evidence. It calibrates the report vocabulary so the machine does not mistake a supporting mechanism for the main listening object.

---

## V4.2 rule

For `莲花园`, the machine-only note over-weighted:

```text
low frequency
pressure
body
narrowing
release / opening
```

The human-calibrated listening priority is:

```text
misty vocal texture
humid atmosphere
Chinese-style memory field
trap / electronic fusion
floating slow pulse
near-field water sound
```

Therefore, P4 must not describe the song as primarily “low”, “body”, or “pressure”. Those can remain as audio evidence, but not as the report center.

---

## Preferred vocabulary

```text
梦幻
雾
古风
trap
mix
缥缈
氛围
宽阔空间
缓拍
降速
暗影
潮湿
水声
未来融合
故障化
```

## Downweighted vocabulary

```text
压迫
低
身体
沉下去
低频身体
释放
打开
退后
```

Downweighted terms are not globally banned. They may appear as measurable evidence, but they should not dominate the listening note unless the human profile explicitly allows them.

---

## Object naming correction

```text
object_03_harmonic_layer
→ 器乐融合度

object_04_vocal_contour_candidate
→ 演唱质感 / 音色湿干 / 边缘清晰模糊

object_02_low_end_body
→ 低频 / 音压 / 冲击节拍 / 敲击 / Beat

object_01_near_rhythmic_pulse
→ 近处的旋律 / 近场感 / groove

object_05_noise_or_texture_mass
→ 合成 / 失真处理 / 故障化 / lofi
```

---

## Report style

The report should keep MSSL spatial language, but every spatial phrase must attach to a concrete listening object.

Good:

```text
水声、庭院感和失真女声一起把空间晕开。
女声 loop 回归后发生循环变形，而不是传统副歌爆发。
器乐先淡出收缩，女声余音延后留在前景。
```

Bad:

```text
压力增强，低频身体接管，空间释放打开。
```

---

## One-sentence calibration

```text
古今梦幻的电子吟唱朦胧诗
```
