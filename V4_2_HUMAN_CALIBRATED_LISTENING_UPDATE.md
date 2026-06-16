# V4.2 Human-Calibrated Listening Update

## Goal

V4.2 adds a P4 human listening-language calibration layer and an optional human comment adapter on top of V4.1 foundation adapters.

This update corrects a key failure in the previous report: the machine over-weighted low-frequency pressure language and under-weighted the actual human listening center.

For `莲花园`, the calibrated center is:

```text
缥缈女声 / 潮湿雾感 / 古风记忆 / trap 电子融合 / 梦幻漂浮 / 水声近场
```

## Changed / added files

```text
scripts/run_full_song_analysis.py
configs/lianhuayuan_p4_human_calibration.json
data/human_comments/netease_lianhuayuan_comments_clean.jsonl
docs/listening_language_layer_draft.md
docs/human_comment_adapter_v4_2.md
outputs/Parodyse_HVRXLD_-_莲花园_full_song_profile_v4_2_human_calibrated.json
outputs/Parodyse_HVRXLD_-_莲花园_full_song_report_v4_2_human_calibrated.md
outputs/netease_lianhuayuan_comment_layer_summary.json
```

## New CLI flags

```text
--human-calibration-profile
--comments-jsonl
```

## New output fields

```text
human_calibration
human_comment_layer
foundation_layer.p4_human_language
human_calibrated_listening_note
machine_listening_report_note
```

## Human comment adapter result for 莲花园

The clean comment export contains 1266 comments. The strongest listener-language anchors include:

```text
梦
水
鬼
月满西楼
莲
采样
莲花
雾
仙
红楼梦
梦核
朦胧
女鬼
悲
妖
```

These anchors support the P4 correction from “pressure / low / body” toward “dream / water / mist / ghostly Chinese memory / electronic fusion”.

## Boundary

The comment layer is a calibration layer, not a popularity score and not a truth oracle. It helps identify repeated human listening-language anchors that the machine report should not ignore.

## Output folder policy update

`run_full_song_analysis.py` now writes each song into its own folder under `outputs/` by default.

```text
outputs/<song-folder>/<input-stem>_full_song_profile.json
outputs/<song-folder>/<input-stem>_full_song_report.md
```

New options:

```text
--output-folder-name  manually set the song folder name
--flat-output         keep the old flat output layout for temporary tests
```

Generated song folders under `outputs/` are ignored by git to avoid accidentally committing copyrighted-song-derived artifacts.
