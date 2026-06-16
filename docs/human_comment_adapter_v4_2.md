# Human Comment Adapter V4.2

Status: optional adapter.

The human comment adapter reads a clean JSONL export of public song comments and extracts listener-language anchors for P4 calibration.

It does not use identities. It should only use fields like:

```text
comment_id
section
content
liked_count
time_str
time_ms
reply_to
```

Avoid storing or publishing unnecessary user fields such as avatar, user ID, IP location, VIP status, or profile metadata.

---

## Role in MSSL

```text
public listener comments
→ anchor term counting
→ listener-language clusters
→ P4 vocabulary calibration
→ MSSL report audit
```

The adapter does not decide whether the machine is “right”. It checks whether human listener language repeatedly points toward a different attention center.

For `莲花园`, the comment layer supports a shift from:

```text
low / pressure / body
```

toward:

```text
梦 / 水 / 鬼 / 月满西楼 / 莲 / 雾 / 仙 / 红楼梦 / 梦核 / 女鬼
```

This matches the human P4 profile’s emphasis on mist, water, Chinese-style memory, floating vocal texture, and electronic fusion.

---

## CLI usage

```powershell
.\.venv\Scripts\python.exe .\scripts\run_full_song_analysis.py `
  --input "D:\歌曲\Parodyse,HVRXLD - 莲花园.wav" `
  --output-dir outputs `
  --human-calibration-profile configs\lianhuayuan_p4_human_calibration.json `
  --comments-jsonl data\human_comments\netease_lianhuayuan_comments_clean.jsonl
```

The raw comment JSONL is local analysis material. Review before publishing a public package.
