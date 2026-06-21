"""P0 professional-audio terminology index for MSSL.

This module is the code-side source of truth for the professional terminology
layer used by the online-AI handoff pipeline.

Axis:
machine proxy -> mechanism evidence -> professional term -> boundary ->
translation affordance.

It intentionally contains terms and boundaries only. It does not read audio,
run LLMs, search the web, identify instruments, recognize lyrics, or make final
music-review claims. Because apparently one must write this down, or a machine
will try to become a tiny music critic with a spreadsheet.
"""

from __future__ import annotations

from typing import Any


PROFESSIONAL_TERM_INDEX: dict[str, dict[str, str]] = {
    "pressure": {
        "machine_field": "perceived_pressure / RMS / peak",
        "professional_term": "perceived loudness / pressure proxy",
        "cn_term": "感知响度 / 压力感代理",
        "domain": "psychoacoustics / dynamics",
        "definition": "Relative subjective-force tendency inferred from energy and spectral weighting proxies.",
        "evidence_basis": "Short-time RMS energy, peak level, onset support, and receiver-side pressure transfer.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not calibrated SPL, not true listener loudness, not emotional pressure truth.",
        "translation_affordance": "贴近、撑满、能量底盘、压近感。",
    },
    "peak": {
        "machine_field": "peak",
        "professional_term": "peak level / transient peak",
        "cn_term": "峰值电平 / 瞬态峰值",
        "domain": "acoustics / digital audio",
        "definition": "Instantaneous amplitude peak or local transient maximum.",
        "evidence_basis": "Peak amplitude regions in the full-mix waveform.",
        "scale": "isolated / present / pronounced / repeated / controlled",
        "boundary": "Does not prove real acoustic peak pressure or mastering quality.",
        "translation_affordance": "瞬间顶出、冲击尖峰、边缘刺出。",
    },
    "dbfs": {
        "machine_field": "dBFS",
        "professional_term": "digital full-scale level reference",
        "cn_term": "数字满刻度电平参考",
        "domain": "digital audio",
        "definition": "Digital level relative to full scale.",
        "evidence_basis": "Digital audio level reference from the file, not acoustic calibration.",
        "scale": "low / moderate / high / near-full-scale",
        "boundary": "Must not be converted to dB SPL without calibration.",
        "translation_affordance": "数字电平高低，不写真实环境多少分贝。",
    },
    "width": {
        "machine_field": "perceived_width / side ratio / mid-side ratio",
        "professional_term": "apparent source width proxy / stereo image width",
        "cn_term": "表观声源宽度代理 / 立体声声像宽度",
        "domain": "spatial / stereo",
        "definition": "Receiver-side estimate of how wide the main stereo image appears.",
        "evidence_basis": "Stereo side-energy, mid-side relation, and interchannel phase coherence proxies.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not physical source width, not room size, not true 3D location.",
        "translation_affordance": "横向打开、声像集中、两侧铺开。",
    },
    "spread": {
        "machine_field": "perceived_spread / side ratio / phase correlation",
        "professional_term": "spatial spread / diffuseness proxy",
        "cn_term": "空间扩散 / 弥散度代理",
        "domain": "spatial / stereo",
        "definition": "How much the field tends to diffuse beyond a compact center image.",
        "evidence_basis": "Side-channel energy, stereo decorrelation, and receiver-side spread transform.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not measured diffuse field and not true listener envelopment by itself.",
        "translation_affordance": "集中变散、边界变雾、背景向外扩开。",
    },
    "envelopment": {
        "machine_field": "envelopment / width / spread",
        "professional_term": "listener envelopment proxy",
        "cn_term": "听者包围感代理",
        "domain": "spatial / receiver-side field",
        "definition": "Receiver-side tendency for the field to wrap around the listener.",
        "evidence_basis": "Combined width, spread, and decorrelation proxies from the stereo mix.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not measured LEV, not VR/HRTF truth, not actual room response.",
        "translation_affordance": "声音有包住听者的趋势。",
    },
    "near_far": {
        "machine_field": "near_far",
        "professional_term": "distance / direct-to-reverberant impression proxy",
        "cn_term": "距离感 / 直达-混响印象代理",
        "domain": "spatial / psychoacoustics",
        "definition": "Whether the foreground reads as close, mid-field, or recessed.",
        "evidence_basis": "Energy, spectral flatness, spread, and receiver-side near/far evidence.",
        "scale": "recessed / mid-field / near-to-mid / close / strongly present",
        "boundary": "No real distance, RT60, BRIR, or room-size claim without measured impulse-response evidence.",
        "translation_affordance": "贴脸、后退、远处、有空间尾巴。",
    },
    "high_low": {
        "machine_field": "spectral_centroid / high_low",
        "professional_term": "spectral centroid / brightness weighting",
        "cn_term": "频谱质心 / 明亮度权重",
        "domain": "MIR / timbre",
        "definition": "Whether spectral energy tends toward low, middle, or upper-frequency brightness.",
        "evidence_basis": "Spectral centroid and high/low band balance relative to the track-local reference range.",
        "scale": "low-weighted / slightly low-weighted / balanced / slightly upper-weighted / upper-weighted",
        "boundary": "Does not identify instrument, genre, emotion, or quality.",
        "translation_affordance": "偏亮、偏暗、重心上移或下沉。",
    },
    "spectral_bandwidth": {
        "machine_field": "spectral_bandwidth",
        "professional_term": "spectral spread / bandwidth",
        "cn_term": "频谱展开 / 带宽",
        "domain": "MIR / timbre",
        "definition": "Dispersion of spectral energy around the spectral centroid.",
        "evidence_basis": "Frequency-domain spread in the full-mix spectrum.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Frequency spread, not stereo width or physical space width.",
        "translation_affordance": "频谱铺开、收束、散开。",
    },
    "spectral_rolloff": {
        "machine_field": "spectral_rolloff",
        "professional_term": "spectral roll-off / high-frequency energy extent",
        "cn_term": "谱滚降 / 高频能量延伸",
        "domain": "MIR / timbre",
        "definition": "Upper-frequency point below which a target proportion of spectral energy is contained.",
        "evidence_basis": "Rolloff frequency or upper-band energy extent.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Does not prove airiness, fidelity, or recording quality.",
        "translation_affordance": "高频延伸、上沿打开、顶部收暗。",
    },
    "spectral_flatness": {
        "machine_field": "spectral_flatness",
        "professional_term": "spectral flatness / noise-likeness",
        "cn_term": "频谱平坦度 / 噪声性",
        "domain": "MIR / timbre texture",
        "definition": "How noise-like or harmonic/peaked the spectrum is.",
        "evidence_basis": "Spectral flatness and harmonic-vs-noise balance proxies.",
        "scale": "tonal / mixed / moderate / noise-like / highly noise-like",
        "boundary": "Noise-like does not mean unwanted noise or bad quality.",
        "translation_affordance": "颗粒、雾化、噪声纹理、非音高化。",
    },
    "spectral_flux": {
        "machine_field": "spectral_flux",
        "professional_term": "spectral change rate / timbral flux",
        "cn_term": "频谱变化率 / 音色通量",
        "domain": "MIR / temporal timbre",
        "definition": "Frame-to-frame spectral change rate.",
        "evidence_basis": "Spectral flux from adjacent analysis frames.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not equal to tempo, rhythm, or real source motion.",
        "translation_affordance": "音色在变、边缘在闪、层在翻动。",
    },
    "band_energy": {
        "machine_field": "low_mid_high_ratio",
        "professional_term": "band energy distribution / spectral tilt",
        "cn_term": "分频段能量分布 / 频谱倾斜",
        "domain": "audio signal processing / psychoacoustics",
        "definition": "Relative weighting across low, mid, and high frequency bands.",
        "evidence_basis": "Low/mid/high band ratios, spectral tilt, and perceptual weighting boundaries.",
        "scale": "low-weighted / mid-forward / high-weighted / balanced",
        "boundary": "Band energy is not direct subjective loudness.",
        "translation_affordance": "低频底盘、中频前景、高频亮边。",
    },
    "low_body": {
        "machine_field": "low_body / low-band ratio",
        "professional_term": "low-frequency foundation / low-order harmonic support",
        "cn_term": "低频基础 / 低次谐波支撑",
        "domain": "timbre / psychoacoustics",
        "definition": "Low-frequency and low-order harmonic support contributing to weight and body.",
        "evidence_basis": "Low-band energy, pressure, and low-order harmonic support proxies.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Does not identify bass, kick, or any physical instrument.",
        "translation_affordance": "下盘、身体感、低频支撑、地基。",
    },
    "onset_strength": {
        "machine_field": "onset_strength",
        "professional_term": "attack strength / transient salience",
        "cn_term": "起振强度 / 瞬态显著性",
        "domain": "MIR / timbre",
        "definition": "Strength of attack-stage energy rise and local transient salience.",
        "evidence_basis": "Onset strength, attack slope, and temporal envelope change.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Does not confirm percussion or an exact instrument.",
        "translation_affordance": "入口硬、边缘利、突然冒出。",
    },
    "onset_density": {
        "machine_field": "onset_density",
        "professional_term": "onset event density / transient density",
        "cn_term": "起音事件密度 / 瞬态密度",
        "domain": "MIR / rhythm",
        "definition": "Density of onset-like events over time.",
        "evidence_basis": "Detected onset activity and transient-event frequency.",
        "scale": "sparse / restrained / moderate / dense / highly dense",
        "boundary": "Not BPM, meter, or rhythm truth by itself.",
        "translation_affordance": "点状事件密、脉冲多、切分感增强。",
    },
    "rhythm": {
        "machine_field": "object_01_near_rhythmic_pulse / onset features",
        "professional_term": "rhythmic articulation / pulse salience",
        "cn_term": "节奏发音清晰度 / 脉冲显著性",
        "domain": "rhythm / temporal articulation",
        "definition": "How clearly recurring pulse or rhythmic articulation is supported by the full mix.",
        "evidence_basis": "Onset strength, percussive proxy, onset density, and object-candidate support.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not beat truth, meter truth, or percussion truth.",
        "translation_affordance": "脉冲清楚、节奏前推、身体被带动。",
    },
    "percussive_proxy": {
        "machine_field": "percussive_proxy",
        "professional_term": "attack-dominant transient profile",
        "cn_term": "起振主导的瞬态轮廓",
        "domain": "timbre / rhythm",
        "definition": "Short-event profile dominated by attack rather than sustained tone.",
        "evidence_basis": "Percussive proxy, onset strength, and transient density.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not a true drum or percussion label.",
        "translation_affordance": "敲击感、短促、颗粒点。",
    },
    "phase_correlation": {
        "machine_field": "phase_correlation",
        "professional_term": "interchannel phase coherence / stereo decorrelation proxy",
        "cn_term": "通道间相位一致性 / 立体声去相关代理",
        "domain": "stereo / spatial",
        "definition": "How coherent or decorrelated the two stereo channels appear.",
        "evidence_basis": "Phase correlation and interchannel similarity proxies.",
        "scale": "decorrelated / partly diffuse / moderate / coherent / strongly coherent",
        "boundary": "Low correlation is not automatically real spaciousness; it may come from mixing or effects.",
        "translation_affordance": "中心稳、声像散、空间漂。",
    },
    "left_right_balance": {
        "machine_field": "left_right_balance / left_right",
        "professional_term": "lateral image bias / interchannel level balance",
        "cn_term": "横向声像偏置 / 通道间声级平衡",
        "domain": "stereo / spatial",
        "definition": "Relative left-right level bias in the stereo image.",
        "evidence_basis": "Interchannel level balance and receiver-side left_right proxy.",
        "scale": "left-leaning / slightly left / centered / slightly right / right-leaning",
        "boundary": "Not a true azimuth estimate or physical source coordinate.",
        "translation_affordance": "偏左、偏右、居中、横向移动。",
    },
    "motion": {
        "machine_field": "perceived_motion / spectral_flux / left_right change",
        "professional_term": "temporal-spectral motion / stereo image movement proxy",
        "cn_term": "时频运动 / 立体声声像运动代理",
        "domain": "motion / temporal-spatial field",
        "definition": "Change in level, spectral activity, or stereo image over time.",
        "evidence_basis": "Perceived motion, spectral flux, dynamic change, and lateral-balance change proxies.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Not real moving source or physical trajectory.",
        "translation_affordance": "推进、摇摆、横向移动、层面变化。",
    },
    "harmonic_proxy": {
        "machine_field": "harmonic_proxy / object_03_harmonic_layer",
        "professional_term": "harmonic structure / tonal support",
        "cn_term": "谐波结构 / 乐音性支撑",
        "domain": "timbre / auditory stream grouping",
        "definition": "Evidence of harmonic or pitch-bearing structure in the full mix.",
        "evidence_basis": "Harmonic proxy, tonal continuity, and harmonic-layer object support.",
        "scale": "reduced / restrained / moderate / pronounced / dominant",
        "boundary": "Does not identify a true instrument, melody, or harmony progression.",
        "translation_affordance": "有可跟踪的乐音骨架。",
    },
    "vocal": {
        "machine_field": "object_04_vocal_contour_candidate / vocal_activity_candidate",
        "professional_term": "vocal-like foreground stream candidate",
        "cn_term": "人声样前景声流候选",
        "domain": "auditory stream grouping / foreground contour",
        "definition": "A foreground stream with vocal-like or lead-line behavior.",
        "evidence_basis": "Mid-band contour, F0-like activity, vocal placeholders, and source-family support.",
        "scale": "reduced / weak / possible / supported / prominent",
        "boundary": "Does not confirm voice, lyrics, singer identity, or ASR content.",
        "translation_affordance": "像人声或主线的前景轮廓。",
    },
    "melody": {
        "machine_field": "lead_line_candidate / F0 / midi_like_skeleton",
        "professional_term": "melodic contour / foreground pitch stream candidate",
        "cn_term": "旋律轮廓 / 前景音高声流候选",
        "domain": "pitch / melodic continuity",
        "definition": "Pitch-bearing continuity that may support a foreground line.",
        "evidence_basis": "F0-like periodicity, MIDI-like reduction, and sequential grouping evidence.",
        "scale": "unclear / weak / possible / supported / prominent",
        "boundary": "Not confirmed main melody, score, lyric, or musical meaning.",
        "translation_affordance": "一条线浮在前面，被耳朵跟住。",
    },
    "object_grouping": {
        "machine_field": "object_candidates",
        "professional_term": "auditory stream grouping candidates",
        "cn_term": "听觉声流分组候选",
        "domain": "auditory scene analysis",
        "definition": "Candidate grouping of full-mix components into plausible auditory streams.",
        "evidence_basis": "Object-candidate scores from full-mix temporal, spectral, and stereo evidence.",
        "scale": "weak / possible / moderate / supported / prominent",
        "boundary": "Not source separation, not true source count, not instrument identity.",
        "translation_affordance": "系统怀疑有几条可分的听觉流。",
    },
}


P0_REVIEW_DECISIONS: tuple[str, ...] = (
    "spectral_bandwidth -> spectral spread / bandwidth, never spatial width",
    "phase_correlation -> interchannel phase coherence / stereo decorrelation proxy",
    "object_candidates -> auditory stream grouping candidates, not source truth",
    "source_family_hypotheses -> source-family grouping hypothesis, not instrument truth",
    "perceived_width -> stereo image width proxy or apparent source width proxy, not physical source width",
    "envelopment -> listener envelopment proxy, not measured LEV or VR/HRTF truth",
)


P0_REVIEW_HOLD: tuple[str, ...] = (
    "MFCC",
    "odd/even harmonic ratio",
    "information masking",
    "measured HRTF / BRIR / RT60 claims",
    "true instrument identification",
    "true lyric or singer identification",
)


def public_professional_term_index() -> list[dict[str, str]]:
    """Return report-safe rows for `online_ai_listening_handoff.md`."""
    rows: list[dict[str, str]] = []
    for key, item in PROFESSIONAL_TERM_INDEX.items():
        rows.append({
            "machine_key": key,
            "machine_field": item["machine_field"],
            "professional_term": item["professional_term"],
            "cn_term": item["cn_term"],
            "domain": item["domain"],
            "definition": item["definition"],
            "evidence_basis": item["evidence_basis"],
            "scale": item["scale"],
            "boundary": item["boundary"],
            "translation_affordance": item["translation_affordance"],
        })
    return rows


def term_spec(machine_key: str) -> dict[str, str]:
    """Fetch a term spec, raising a clear error for missing index entries."""
    try:
        return PROFESSIONAL_TERM_INDEX[machine_key]
    except KeyError as exc:
        raise KeyError(f"Missing professional term index entry: {machine_key}") from exc


def p0_policy() -> dict[str, Any]:
    """Return P0 decisions for code and docs consistency checks."""
    return {
        "axis": "machine proxy -> professional audio term -> boundary -> translation affordance",
        "review_decisions": list(P0_REVIEW_DECISIONS),
        "hold_for_review": list(P0_REVIEW_HOLD),
        "default_boundary": "MSSL emits professional descriptors and candidates, not source truth, lyric truth, emotion truth, or room truth.",
    }
