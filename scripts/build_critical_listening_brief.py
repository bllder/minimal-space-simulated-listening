"""Manual critical-listening brief builder for full-song MSSL JSON.

Optional bridge only: MSSL evidence -> critical brief -> external LLM criticism.
It does not read audio and does not generate the final review.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

OBJ = {
    "object_04_vocal_contour_candidate": "foreground vocal/flow line",
    "object_03_harmonic_layer": "harmonic / chamber-like surrounding field",
    "object_02_low_end_body": "low-end body",
    "object_01_near_rhythmic_pulse": "near rhythmic pulse",
    "object_05_noise_or_texture_mass": "texture / edge haze",
}
E = ("perceived_pressure", "perceived_width", "perceived_spread", "near_far", "high_low", "envelopment")
PROMPT = """请根据下面的 MSSL critical listening brief，写一篇中文 close-listening 乐评。

如果用户另行提供带时间戳歌词，可以把它作为外部文本材料；不要自行搜索、补全或确认歌词内容。

要求：
不要解释 MSSL，不要逐项复述字段，不要写成技术报告。
先提出一个明确的核心听感判断，再展开声音如何成立。
把证据压缩成 3–5 个听感运动，而不是按 segment 流水账。
可以写空间、层次、flow / 人声轮廓、低频、和声层、节奏推进、风格行为、情绪倾向。
但不要声称你听过原始音频，不要确认歌手身份、歌词内容、精确乐器、权威流派或真实情绪。
情绪词和风格词可以出现，但必须写成由听感证据支持的判断，而不是绝对真值。
允许指出作品的有效处、风险处、单调处或特别处。
最终文本应像音乐评论，不像分析报告。
"""
GUIDE = [
    "Do not explain MSSL.",
    "Do not list raw segment fields.",
    "Start with a critical listening thesis.",
    "Compress evidence into aesthetic movements.",
    "Write like close-listening music criticism, not a technical report.",
    "Use uncertainty once in the method note, not in every sentence.",
    "Every strong claim must be traceable to evidence.",
    "Do not search, invent, or confirm lyrics; use lyrics only if the user supplied them as external material.",
    "Do not claim lyrics, singer identity, exact instruments, genre truth, or emotion truth.",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build critical_listening_brief.json from full-song MSSL JSON.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--min-movements", type=int, default=3)
    parser.add_argument("--max-movements", type=int, default=5)
    args = parser.parse_args()

    src = Path(args.input)
    profile = json.loads(src.read_text(encoding="utf-8"))
    brief = build(profile, src, args.min_movements, args.max_movements)
    out = Path(args.output_dir) if args.output_dir else src.parent
    out.mkdir(parents=True, exist_ok=True)
    (out / "critical_listening_brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "critical_listening_prompt_input.md").write_text(
        f"{PROMPT}\n\n## MSSL critical listening brief\n\n```json\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n```\n",
        encoding="utf-8",
    )
    print(f"Wrote {out / 'critical_listening_brief.json'}")
    print(f"Wrote {out / 'critical_listening_prompt_input.md'}")


def build(profile: dict[str, Any], src: Path, min_m: int, max_m: int) -> dict[str, Any]:
    raw = profile.get("segments") or profile.get("segment_evidence") or []
    if not isinstance(raw, list) or not raw:
        raise ValueError("Expected non-empty segments or segment_evidence.")
    cards = [card(seg, i) for i, seg in enumerate(raw) if isinstance(seg, dict)]
    summary = summarize(profile, cards)
    mvs = movements(cards, min_m, max_m)
    return {
        "version": "mssl_critical_listening_brief_v0_2",
        "status": "manual_optional_bridge_not_default_pipeline",
        "source_profile": {
            "path": str(src),
            "analysis_label": profile.get("analysis_label"),
            "source_version": profile.get("version"),
            "segment_count": len(cards),
        },
        "boundary": {
            "does_not_read_audio": True,
            "does_not_generate_final_review": True,
            "does_not_do_asr": True,
            "does_not_do_singer_identity": True,
            "does_not_do_instrument_truth": True,
            "does_not_do_genre_truth": True,
            "does_not_do_emotion_truth": True,
            "does_not_search_or_confirm_lyrics": True,
        },
        "central_thesis_candidates": theses(summary, mvs),
        "macro_movements": mvs,
        "dominant_listening_objects": objects(cards),
        "tensions": tensions(summary, mvs),
        "risks_or_limits": risks(profile, summary),
        "llm_writing_guidance": {"rules": GUIDE},
    }


def card(seg: dict[str, Any], i: int) -> dict[str, Any]:
    tr = seg.get("time_range") or {}
    return {
        "segment_id": str(seg.get("segment_id") or f"segment_{i + 1:02d}"),
        "time_label": str(tr.get("label") or f"{clock(num(tr.get('start_seconds')))}-{clock(num(tr.get('end_seconds')))}"),
        "e": fd(path(seg, ["ome_mapping", "e_space_receiver_side"]) or {}),
        "obj": fd(path(seg, ["object_candidates", "scores"]) or {}),
        "role": str(path(seg, ["musical_structure", "role_label"]) or "section_like"),
        "phrase": str(path(seg, ["midi_like_skeleton", "phrase_shape"]) or "unknown"),
    }


def summarize(profile: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, Any]:
    roles: dict[str, int] = {}
    for c in cards:
        roles[c["role"]] = roles.get(c["role"], 0) + 1
    return {
        "role_counts": roles,
        "role_diversity": len(roles),
        "object_means": {k: avg(c["obj"].get(k) for c in cards) for k in OBJ},
        "e_means": {k: avg(c["e"].get(k) for c in cards) for k in E},
        "style_status": path(profile, ["policy", "style_status"]),
        "mssl_boundary": path(profile, ["policy", "mssl_boundary"]),
    }


def movements(cards: list[dict[str, Any]], min_m: int, max_m: int) -> list[dict[str, Any]]:
    if len(cards) <= 3:
        groups, scores = [[c] for c in cards], [0.0] * len(cards)
    else:
        bounds, by_bound = choose_boundaries(cards, target_count(cards, min_m, max_m))
        groups = [cards[bounds[i] : bounds[i + 1]] for i in range(len(bounds) - 1)]
        scores = [0.0] + [by_bound.get(b, 0.0) for b in bounds[1:-1]]

    drafted = []
    prev = None
    for i, group in enumerate(groups):
        gs = gsummary(group)
        drafted.append({"group": group, "summary": gs, "label": mlabel(i, len(groups), gs, prev), "entry_change_score": scores[i]})
        prev = gs

    merged = merge_same_label_runs(drafted, min_m)
    out, prev = [], None
    for i, item in enumerate(merged):
        group, gs = item["group"], item["summary"]
        label = mlabel(i, len(merged), gs, prev)
        top = ", ".join(x["object"] for x in gs["dominant_objects"][:2]) or "available listening objects"
        out.append({
            "time_range": span(group),
            "label": label,
            "listening_action": action(label, top),
            "supporting_segments": [c["segment_id"] for c in group],
            "grouping": {"method": "evidence_change_points", "entry_change_score": round(num(item.get("entry_change_score")), 4)},
            "evidence_summary": gs,
            "confidence": conf(gs, len(group), num(item.get("entry_change_score"))),
            "not_proven": ["formal verse/chorus truth", "producer intent", "lyrics-driven interpretation"],
        })
        prev = gs
    return out


def target_count(cards: list[dict[str, Any]], min_m: int, max_m: int) -> int:
    n = len(cards)
    base = 3 if n <= 10 else 4 if n <= 18 else 5
    return min(n, max(max(1, min_m), min(max(max_m, min_m), base)))


def choose_boundaries(cards: list[dict[str, Any]], target: int) -> tuple[list[int], dict[int, float]]:
    n = len(cards)
    min_span = 1 if n <= target * 2 else 2
    changes = [(i, segment_change(cards[i - 1], cards[i])) for i in range(1, n)]
    selected: list[int] = []
    scores: dict[int, float] = {}
    for idx, score in sorted(changes, key=lambda item: item[1], reverse=True):
        if len(selected) >= target - 1:
            break
        trial = sorted(selected + [idx])
        if all(b - a >= min_span for a, b in zip([0] + trial, trial + [n])):
            selected.append(idx)
            scores[idx] = score
    q, by_idx = 1, dict(changes)
    while len(selected) < target - 1 and q < target:
        idx = round(q * n / target)
        if 0 < idx < n and idx not in selected:
            selected.append(idx)
            scores[idx] = by_idx.get(idx, 0.0)
        q += 1
    return [0] + sorted(selected) + [n], scores


def segment_change(a: dict[str, Any], b: dict[str, Any]) -> float:
    weights = {"perceived_pressure": 0.30, "perceived_width": 0.30, "perceived_spread": 0.15, "near_far": 0.10, "high_low": 0.08, "envelopment": 0.12}
    score = sum(abs(num(a["e"].get(k)) - num(b["e"].get(k))) * w for k, w in weights.items())
    score += 0.06 if a["role"] != b["role"] else 0.0
    score += 0.04 if a["phrase"] != b["phrase"] else 0.0
    score += 0.06 if obj_sig(a) != obj_sig(b) else 0.0
    return round(score, 4)


def obj_sig(c: dict[str, Any]) -> tuple[str, ...]:
    vals = [(k, num(c["obj"].get(k))) for k in OBJ]
    return tuple(k for k, _ in sorted(vals, key=lambda item: item[1], reverse=True)[:2])


def merge_same_label_runs(items: list[dict[str, Any]], min_m: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if out and len(out) > min_m - 1 and out[-1]["label"] == item["label"]:
            out[-1]["group"].extend(item["group"])
            out[-1]["summary"] = gsummary(out[-1]["group"])
            out[-1]["entry_change_score"] = max(num(out[-1].get("entry_change_score")), num(item.get("entry_change_score")))
        else:
            out.append(item)
    return out


def gsummary(group: list[dict[str, Any]]) -> dict[str, Any]:
    e = {k: avg(c["e"].get(k) for c in group) for k in E}
    objs = {OBJ[k]: avg(c["obj"].get(k) for c in group) for k in OBJ}
    roles: dict[str, int] = {}
    phrases: dict[str, int] = {}
    for c in group:
        roles[c["role"]] = roles.get(c["role"], 0) + 1
        phrases[c["phrase"]] = phrases.get(c["phrase"], 0) + 1
    return {
        "field": {"pressure": e["perceived_pressure"], "width": e["perceived_width"], "spread": e["perceived_spread"], "near_far": e["near_far"], "brightness_height": e["high_low"], "envelopment": e["envelopment"]},
        "dominant_objects": [{"object": n, "mean_support": v} for n, v in sorted(objs.items(), key=lambda item: item[1], reverse=True)[:3]],
        "section_roles": roles,
        "phrase_shapes": phrases,
    }


def mlabel(i: int, total: int, gs: dict[str, Any], prev: dict[str, Any] | None) -> str:
    f = gs["field"]
    pf = (prev or {}).get("field", {})
    pd, wd = f["pressure"] - pf.get("pressure", f["pressure"]), f["width"] - pf.get("width", f["width"])
    top = {x["object"]: x["mean_support"] for x in gs["dominant_objects"]}
    if i == 0:
        return "field establishment"
    if i == total - 1 and wd > 0.04 and f["pressure"] >= 0.75:
        return "residual widening under pressure"
    if i == total - 1 and (pd < -0.08 or wd > 0.05) and f["pressure"] < 0.75:
        return "release / residual opening"
    if f["pressure"] > 0.75 and f["width"] < 0.35:
        return "center compression"
    if wd > 0.08 and f["pressure"] >= 0.75:
        return "pressurized spatial widening"
    if wd > 0.08:
        return "spatial re-expansion"
    if f["pressure"] >= 0.75:
        return "pressurized continuation"
    if top.get("foreground vocal/flow line", 0.0) >= 0.50:
        return "foreground flow concentration"
    if top.get("low-end body", 0.0) >= 0.50 or top.get("near rhythmic pulse", 0.0) >= 0.45:
        return "pressure-driven continuation"
    return "field continuation"


def action(label: str, top: str) -> str:
    return {
        "field establishment": f"The opening establishes a listening field around {top}.",
        "center compression": f"The field narrows around {top}; pressure matters more than section contrast.",
        "pressurized continuation": f"{top} keep the field active through sustained pressure rather than a clean reset.",
        "pressurized spatial widening": f"The field widens around {top}, but pressure remains part of the movement.",
        "spatial re-expansion": f"The field opens around {top}, turning width into movement.",
        "foreground flow concentration": f"Attention gathers around {top}; the foreground line carries the argument.",
        "pressure-driven continuation": f"{top} keep propulsion active without a strong formal reset.",
        "residual widening under pressure": f"The ending opens the field around {top} without fully releasing pressure.",
        "release / residual opening": f"The field loosens and leaves {top} as residual carriers.",
    }.get(label, f"The section continues the established field through {top}.")


def objects(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for k, name in OBJ.items():
        vals = [num(c["obj"].get(k)) for c in cards]
        mean, peak = avg(vals), max(vals) if vals else 0.0
        if mean < 0.30 and peak < 0.48:
            continue
        sup = [c for c in cards if num(c["obj"].get(k)) >= max(0.38, mean)]
        out.append({
            "object": name,
            "role_in_listening": f"{'dominant' if mean >= 0.55 else 'recurrent' if peak >= 0.50 else 'supporting'} listening object; usable as behavior, not identity truth",
            "behavior": behavior(name),
            "relation_to_other_objects": relation(name),
            "evidence_support": {"mean_support": mean, "peak_support": peak, "supporting_segments": refs(sup[:8])},
            "not_proven": limits(name),
        })
    return sorted(out, key=lambda x: x["evidence_support"]["mean_support"], reverse=True)


def behavior(name: str) -> str:
    return {
        "foreground vocal/flow line": "tracks as foreground contour without proving words or performer identity",
        "harmonic / chamber-like surrounding field": "frames the foreground as enclosure rather than decoration only",
        "low-end body": "grounds pressure and body without proving an exact bass instrument",
        "near rhythmic pulse": "organizes forward movement through recurrence and near pressure",
        "texture / edge haze": "softens or roughens object edges",
    }.get(name, "acts as a bounded listening object")


def relation(name: str) -> str:
    return {
        "foreground vocal/flow line": "can be framed by harmonic field and pressed by body/pulse evidence",
        "harmonic / chamber-like surrounding field": "can surround and scale the foreground line",
        "low-end body": "can pair with rhythmic pulse as body-propulsion support",
        "near rhythmic pulse": "can press against foreground and harmonic layers",
        "texture / edge haze": "can mask object boundaries",
    }.get(name, "relation remains evidence-limited")


def theses(summary: dict[str, Any], mvs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    o, e, labels = summary["object_means"], summary["e_means"], {m["label"] for m in mvs}
    out = []
    if e["perceived_width"] >= 0.30 and ({"center compression", "spatial re-expansion", "pressurized spatial widening", "residual widening under pressure"} & labels):
        out.append(thesis("space acts as propulsion rather than decoration", "Pressure/width changes can organize form.", e["perceived_width"], e["perceived_pressure"]))
    if o["object_04_vocal_contour_candidate"] >= 0.42 and o["object_03_harmonic_layer"] >= 0.42:
        out.append(thesis("foreground vocal/flow line is framed by a chamber-like harmonic field", "Foreground contour and harmonic field recur together.", o["object_04_vocal_contour_candidate"], o["object_03_harmonic_layer"]))
    if {"center compression", "pressurized spatial widening", "residual widening under pressure"} & labels:
        out.append(thesis("the song works through compression and pressure-managed widening, not chorus-like contrast", "The movement map is organized by pressure/width shifts.", 0.64, 0.68, ["formal chorus/verse truth", "producer intent"]))
    if o["object_02_low_end_body"] >= 0.42 or o["object_01_near_rhythmic_pulse"] >= 0.38:
        out.append(thesis("low-end body and near rhythmic pulse do structural work, not just backing support", "Body or pulse support can become critical listening material.", o["object_02_low_end_body"], o["object_01_near_rhythmic_pulse"], ["exact bass/drum source", "mixing intent"]))
    return out[:4] or [thesis("the song is best approached through object relations rather than raw segment labels", "Dominant objects are clearer than formal section truth in this evidence.", 0.55, 0.55)]


def thesis(text: str, support: str, a: float, b: float, no: list[str] | None = None) -> dict[str, Any]:
    return {"thesis": text, "evidence_support": support, "confidence": round(min(0.86, 0.38 + avg([a, b]) * 0.48), 4), "not_proven": no or ["taste judgment", "genre truth", "emotion truth", "lyrics or performer identity"]}


def tensions(summary: dict[str, Any], mvs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    o, e, rd, labels = summary["object_means"], summary["e_means"], summary["role_diversity"], {m["label"] for m in mvs}
    out = []
    if o["object_03_harmonic_layer"] >= 0.40 and e["perceived_pressure"] >= 0.42:
        out.append(tension("elegant harmonic field vs near-body pressure", "Harmonic support and pressure evidence coexist.", o["object_03_harmonic_layer"], e["perceived_pressure"]))
    if o["object_04_vocal_contour_candidate"] >= 0.42 and rd <= 3:
        out.append(tension("dense vocal/flow motion vs relatively stable section structure", "Foreground contour evidence can remain active while section labels repeat.", 0.62, 0.70, ["actual syllable density", "word content", "formal section truth"]))
    if e["perceived_width"] >= 0.30 and e["perceived_pressure"] >= 0.42:
        out.append(tension("wide stereo environment vs centered foreground compression", "Width and pressure are both present as evidence.", e["perceived_width"], e["perceived_pressure"]))
    if labels & {"pressurized continuation", "residual widening under pressure"} and rd <= 3:
        out.append(tension("pressure continuity vs weak formal contrast", "Pressure/body/pulse can sustain movement even when formal contrast is not strong.", 0.58, 0.66, ["weakness as value judgment", "composition intent"]))
    return out[:4]


def tension(text: str, evidence: str, a: float, b: float, no: list[str] | None = None) -> dict[str, Any]:
    return {"tension": text, "evidence_summary": evidence, "confidence": round(min(0.86, 0.38 + avg([a, b]) * 0.48), 4), "not_proven": no or ["authorial intent", "absolute affect truth", "exact instrument truth"]}


def risks(profile: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    out = [
        "instrument identity cannot be asserted without stem-backed adapter evidence",
        "emotion words must remain affective tendencies, not truth labels",
        "genre or style words must be style behavior, not authoritative genre truth",
        "lyrics and performer identity cannot be claimed unless supplied by a separate trusted source",
        "do not search, invent, or confirm lyrics from this brief",
    ]
    if summary["role_diversity"] <= 3:
        out.insert(0, "formal section contrast appears weak or repetitive in available heuristic evidence")
    if summary.get("style_status"):
        out.append(f"style status: {summary['style_status']}")
    if summary.get("mssl_boundary"):
        out.append(f"MSSL boundary: {summary['mssl_boundary']}")
    sep = path(profile, ["optional_adapters", "source_separation", "status"])
    if sep:
        out.append(f"source separation status: {sep}")
    return out


def limits(name: str) -> list[str]:
    return ["performer identity", "word content", "isolated stem truth"] if name == "foreground vocal/flow line" else ["exact source identity", "authorial intent"]


def conf(gs: dict[str, Any], n: int, entry_change_score: float) -> float:
    top = max((x["mean_support"] for x in gs["dominant_objects"]), default=0.0)
    total = sum(gs["section_roles"].values()) or 1
    role_clarity = max(gs["section_roles"].values(), default=0) / total
    value = 0.42 + top * 0.16 + role_clarity * 0.10 + min(1.0, entry_change_score * 3.0) * 0.14 + min(n, 8) / 8.0 * 0.08
    return round(min(0.86, max(0.45, value)), 4)


def span(group: list[dict[str, Any]]) -> str:
    return f"{group[0]['time_label'].split('-')[0]}-{group[-1]['time_label'].split('-')[-1]}"


def refs(cards: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"segment_id": c["segment_id"], "time_range": c["time_label"]} for c in cards]


def fd(value: Any) -> dict[str, float]:
    return {str(k): num(v) for k, v in value.items() if v is not None} if isinstance(value, dict) else {}


def path(value: dict[str, Any], keys: list[str]) -> Any:
    cur: Any = value
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def avg(values: Any) -> float:
    vals = [num(v) for v in values]
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def num(value: Any) -> float:
    try:
        x = 0.0 if value is None else float(value)
    except (TypeError, ValueError):
        return 0.0
    return x if math.isfinite(x) else 0.0


def clock(sec: float) -> str:
    sec = max(0.0, sec)
    minutes, seconds = int(sec // 60), int(round(sec % 60))
    if seconds >= 60:
        minutes += 1
        seconds -= 60
    return f"{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    main()
