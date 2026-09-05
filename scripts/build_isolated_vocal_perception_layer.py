#!/usr/bin/env python3
"""Build bounded perceptual proxies from an isolated singing voice.

This is not an aesthetic judge. It measures phrase-level acoustic behavior and
produces traceable perceptual proxies that may later be calibrated with human
A/B judgements. Use on dry/isolated or strongly vocal-dominant audio only.
"""
from __future__ import annotations
import argparse, json, math, wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np

EPS=1e-12
DEFAULT_JSON="isolated_vocal_perception_layer.json"
DEFAULT_MD="isolated_vocal_perception_layer.md"

@dataclass(frozen=True)
class TimeRange:
    label:str; start:float; end:float


def clamp01(x:float)->float: return float(min(1,max(0,x)))
def db(x:float)->float: return 20*math.log10(max(abs(x),EPS))

def read_pcm_wav_mono(path:Path):
    with wave.open(str(path),"rb") as w:
        ch,sw,sr,n=w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes(); raw=w.readframes(n)
    if sw==1:
        x=(np.frombuffer(raw,np.uint8).astype(float)-128)/128
    elif sw==2:
        x=np.frombuffer(raw,"<i2").astype(float)/32768
    elif sw==4:
        x=np.frombuffer(raw,"<i4").astype(float)/2147483648
    else: raise ValueError(f"Unsupported PCM width: {sw}")
    x=x[:len(x)-len(x)%ch].reshape(-1,ch).mean(1).astype(np.float32)
    return x,sr,{"path":str(path),"sample_rate":sr,"channels":ch,"duration_seconds":round(len(x)/sr,6)}

def frames(x,n,hop):
    if len(x)<n: x=np.pad(x,(0,n-len(x)))
    count=1+(len(x)-n)//hop
    return np.lib.stride_tricks.as_strided(x,shape=(count,n),strides=(x.strides[0]*hop,x.strides[0])).copy()

def rms_series(x,sr):
    n=max(64,int(.032*sr)); hop=max(32,int(.01*sr)); f=frames(x,n,hop)
    r=np.sqrt(np.mean(f.astype(float)**2,1)+EPS); t=(np.arange(len(r))*hop+n/2)/sr
    return t,20*np.log10(np.maximum(r,EPS))

def auto_threshold(v):
    peak=float(np.percentile(v,99.5)); floor=float(np.percentile(v,18)); return min(max(floor+10,peak-31),peak-12)

def detect_phrases(x,sr,threshold):
    t,v=rms_series(x,sr); mask=v>=threshold; step=float(np.median(np.diff(t))) if len(t)>1 else .01
    raw=[]; start=None
    for ti,on in zip(t,mask):
        if on and start is None: start=max(0,float(ti-step/2))
        elif not on and start is not None: raw.append((start,float(ti-step/2))); start=None
    if start is not None: raw.append((start,float(t[-1]+step/2)))
    merged=[]
    for a,b in raw:
        if merged and a-merged[-1][1]<=.65: merged[-1]=(merged[-1][0],b)
        else: merged.append((a,b))
    return [TimeRange(f"phrase_{i:03d}",a,b) for i,(a,b) in enumerate(merged,1) if b-a>=.75]

def group_takes(ps):
    if not ps:return []
    groups=[]; a=ps[0].start; b=ps[0].end
    for p in ps[1:]:
        if p.start-b>=10:
            if b-a>=15: groups.append((a,b))
            a=p.start
        b=p.end
    if b-a>=15: groups.append((a,b))
    if not groups: groups=[(ps[0].start,ps[-1].end)]
    return [TimeRange(f"take_{i:02d}",a,b) for i,(a,b) in enumerate(groups,1)]

def cut(x,sr,a,b): return x[max(0,int(a*sr)):min(len(x),int(b*sr))]

def envelope(seg,sr):
    _,v=rms_series(seg,sr); q10,q50,q90=np.percentile(v,[10,50,90]); thirds=np.array_split(v,3)
    m=[float(np.median(z)) for z in thirds]; k=max(1,len(v)//5)
    return {"rms_dbfs_median":round(float(q50),3),"dynamic_range_80_db":round(float(q90-q10),3),"first_middle_last_dbfs":[round(z,3) for z in m],"peak_position_0_1":round(int(np.argmax(v))/max(1,len(v)-1),4),"attack_to_median_db":round(float(np.percentile(v[:k],75)-q50),3),"release_to_median_db":round(float(np.percentile(v[-k:],75)-q50),3),"envelope_arc_db":round(m[1]-.5*(m[0]+m[2]),3)}

def spectrum(seg,sr):
    n=max(256,int(.046*sr)); hop=max(128,int(.023*sr)); f=frames(seg,n,hop)*np.hanning(n); p=np.abs(np.fft.rfft(f,axis=1))**2+EPS; hz=np.fft.rfftfreq(n,1/sr); total=p.sum(1)+EPS
    c=(p*hz).sum(1)/total; highmask=hz>=300; c300=(p[:,highmask]*hz[highmask]).sum(1)/(p[:,highmask].sum(1)+EPS)
    return {"spectral_centroid_median_hz":round(float(np.median(c)),3),"spectral_centroid_above300_median_hz":round(float(np.median(c300)),3),"spectral_centroid_std_hz":round(float(np.std(c300)),3)}

def pitch(seg,sr):
    target=16000
    if sr!=target:
        old=np.linspace(0,1,len(seg),endpoint=False); new=np.linspace(0,1,max(1,int(len(seg)*target/sr)),endpoint=False); seg=np.interp(new,old,seg); sr=target
    n=int(.05*sr); hop=int(.02*sr); f=frames(seg,n,hop); lmin=max(1,int(sr/700)); lmax=min(n-2,int(sr/70)); hz=[]; per=[]
    for row in f:
        row=(row-row.mean())*np.hanning(n); ac=np.correlate(row,row,"full")[n-1:]
        if ac[0]<=EPS: hz.append(np.nan); per.append(0); continue
        r=ac[lmin:lmax+1]/ac[0]; j=int(np.argmax(r)); q=float(r[j]); per.append(q); hz.append(sr/(lmin+j) if q>=.22 else np.nan)
    hz=np.asarray(hz,float); per=np.asarray(per,float); valid=np.isfinite(hz)&(per>=.26)
    if valid.sum()<3:return {"voiced_frame_ratio":0,"median_f0_hz":None,"pitch_range_90_semitones":None,"pitch_median_step_semitones":None,"periodicity_median":round(float(np.median(per)),6)}
    midi=69+12*np.log2(hz[valid]/440); d=np.abs(np.diff(midi)); d=d[d<7]
    return {"voiced_frame_ratio":round(float(valid.mean()),6),"median_f0_hz":round(float(np.median(hz[valid])),3),"pitch_range_90_semitones":round(float(np.percentile(midi,95)-np.percentile(midi,5)),3),"pitch_median_step_semitones":round(float(np.median(d)),4) if len(d) else 0,"periodicity_median":round(float(np.median(per[valid])),6)}

def proxies(ev):
    e,s,p=ev["envelope"],ev["spectrum"],ev["pitch_contour"]; pr=float(p.get("periodicity_median") or 0); vr=float(p.get("voiced_frame_ratio") or 0); rng=float(p.get("pitch_range_90_semitones") or 0); step=float(p.get("pitch_median_step_semitones") or 0); dyn=float(e.get("dynamic_range_80_db") or 0); arc=abs(float(e.get("envelope_arc_db") or 0)); cen=float(s.get("spectral_centroid_above300_median_hz") or 0); move=float(s.get("spectral_centroid_std_hz") or 0)
    vals={"harmonic_stability_proxy":clamp01((pr-.22)/.55)*clamp01(vr/.75),"pitch_mobility_proxy":clamp01(.7*rng/10+.3*step/1.3),"dynamic_mobility_proxy":clamp01(.75*dyn/18+.25*arc/8),"spectral_mobility_proxy":clamp01(move/1000),"brightness_proxy":clamp01((cen-650)/1800),"noise_air_proxy":clamp01(1-pr)}
    vals["expressive_salience_proxy"]=clamp01(.29*vals["pitch_mobility_proxy"]+.31*vals["dynamic_mobility_proxy"]+.2*vals["spectral_mobility_proxy"]+.1*abs(float(e["attack_to_median_db"]))/9+.1*abs(float(e["release_to_median_db"]))/9)
    boundary={"expressive_salience_proxy":"Local organized change, not emotion/beauty/infectiousness.","brightness_proxy":"Mic/EQ/distance can change this.","noise_air_proxy":"Do not equate directly with breathiness or health."}
    return {k:{"value":round(float(v),6),"boundary":boundary.get(k,"Perceptual proxy only; not an aesthetic or technique verdict.")} for k,v in vals.items()}

def analyze(seg,sr):
    rms=float(np.sqrt(np.mean(seg.astype(float)**2)+EPS)); peak=float(np.max(np.abs(seg))+EPS)
    ev={"level":{"rms_dbfs":round(db(rms),3),"peak_dbfs":round(db(peak),3),"crest_factor_db":round(db(peak/rms),3)},"envelope":envelope(seg,sr),"spectrum":spectrum(seg,sr),"pitch_contour":pitch(seg,sr)}
    return ev,proxies(ev)

def aggregate(rows):
    out={}; keys=rows[0].keys() if rows else []
    for k in keys:
        v=[float(r[k]["value"]) for r in rows]; out[k]={"value":round(float(np.median(v)),6),"p25":round(float(np.percentile(v,25)),6),"p75":round(float(np.percentile(v,75)),6)}
    return out

def build_layer(x,sr,meta=None,label=None,threshold=None,takes=None):
    _,rv=rms_series(x,sr); threshold=float(threshold) if threshold is not None else auto_threshold(rv); ps=detect_phrases(x,sr,threshold); takes=takes or group_takes(ps)
    rows=[]
    for p in ps:
        center=(p.start+p.end)/2; take=next((t.label for t in takes if t.start<=center<=t.end),"unassigned"); ev,pv=analyze(cut(x,sr,p.start,p.end),sr)
        rows.append({"phrase_id":p.label,"take_id":take,"start":round(p.start,4),"end":round(p.end,4),"duration":round(p.end-p.start,4),"acoustic_evidence":ev,"perceptual_proxy_vector":pv})
    summaries=[]
    for t in takes:
        m=[r for r in rows if r["take_id"]==t.label]; hot=sorted(m,key=lambda r:r["perceptual_proxy_vector"]["expressive_salience_proxy"]["value"],reverse=True)[:5]
        summaries.append({"take_id":t.label,"start":round(t.start,4),"end":round(t.end,4),"phrase_count":len(m),"aggregate_proxy_vector":aggregate([r["perceptual_proxy_vector"] for r in m]),"expressive_salience_hotspots":[{"phrase_id":r["phrase_id"],"start":r["start"],"end":r["end"],"value":r["perceptual_proxy_vector"]["expressive_salience_proxy"]["value"]} for r in hot]})
    return {"version":"isolated_vocal_perception_layer_v0_1_local_proxies","status":"computed_from_local_isolated_vocal_acoustic_proxies","layer_role":"isolated singing voice -> phrase evidence -> bounded perceptual proxies -> future human calibration","analysis_label":label,"source":meta or {},"input_contract":{"expected":"isolated/dry vocal or strongly vocal-dominant recording","not_expected":"normal full mix with accompaniment"},"activity_threshold_dbfs":round(threshold,4),"take_count":len(takes),"phrase_count":len(rows),"takes":[{"take_id":t.label,"start":round(t.start,4),"end":round(t.end,4)} for t in takes],"phrases":rows,"take_summaries":summaries,"human_calibration_interface":{"status":"not_calibrated","preferred_training_form":"pairwise preference / A-B judgement","future_target":"learn evidence/proxy vectors -> listener/panel preference probability"},"unsupported_absolute_judgements":["beautiful_or_ugly_timbre","emotion_truth","infectiousness_or_movingness","vocal_technique_diagnosis","healthy_or_unhealthy_phonation","professional_quality_score"],"truth_boundary":"This layer measures acoustic behavior and bounded perceptual proxies. Absolute subjective judgements require human calibration and should remain probabilistic after calibration."}

def render_md(d):
    lines=["# Isolated Vocal Perception Layer","",f"- takes: **{d['take_count']}**",f"- phrases: **{d['phrase_count']}**",f"- threshold: **{d['activity_threshold_dbfs']} dBFS**",""]
    for t in d["take_summaries"]:
        lines += [f"## {t['take_id']} — {t['start']:.2f}s to {t['end']:.2f}s",""]+[f"- `{k}`: {v['value']:.3f} (IQR {v['p25']:.3f}–{v['p75']:.3f})" for k,v in t["aggregate_proxy_vector"].items()]+[""]
    lines += ["## What this layer cannot say",""]+[f"- `{x}`" for x in d["unsupported_absolute_judgements"]]+["","## Human calibration","","Preferred next step: pairwise A/B human judgements, not pretending proxy scores are aesthetic truth.","","## Truth boundary","",d["truth_boundary"],""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output-dir",default=None); ap.add_argument("--analysis-label",default=None); ap.add_argument("--activity-threshold-db",type=float,default=None); a=ap.parse_args(); p=Path(a.input); x,sr,meta=read_pcm_wav_mono(p); d=build_layer(x,sr,meta,a.analysis_label or p.stem,a.activity_threshold_db); out=Path(a.output_dir) if a.output_dir else p.parent; out.mkdir(parents=True,exist_ok=True); (out/DEFAULT_JSON).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8"); (out/DEFAULT_MD).write_text(render_md(d),encoding="utf-8"); print(f"Wrote {out/DEFAULT_JSON}"); print(f"Wrote {out/DEFAULT_MD}")
if __name__=="__main__": main()
