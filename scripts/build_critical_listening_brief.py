"""Manual critical-listening brief builder for full-song MSSL JSON.

Optional bridge only: MSSL evidence -> critical brief -> external LLM criticism.
It does not read audio and does not generate the final review.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from typing import Any

OBJ={"object_04_vocal_contour_candidate":"foreground vocal/flow line","object_03_harmonic_layer":"harmonic / chamber-like surrounding field","object_02_low_end_body":"low-end body","object_01_near_rhythmic_pulse":"near rhythmic pulse","object_05_noise_or_texture_mass":"texture / edge haze"}
E=("perceived_pressure","perceived_width","perceived_spread","near_far","high_low","envelopment")
PROMPT="""请根据下面的 MSSL critical listening brief，可以结合搜索时间戳的歌词，写一篇中文 close-listening 乐评。

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
GUIDE=["Do not explain MSSL.","Do not list raw segment fields.","Start with a critical listening thesis.","Compress evidence into aesthetic movements.","Write like close-listening music criticism, not a technical report.","Use uncertainty once in the method note, not in every sentence.","Every strong claim must be traceable to evidence.","Do not claim lyrics, singer identity, exact instruments, genre truth, or emotion truth."]


def main()->None:
    p=argparse.ArgumentParser(description="Build critical_listening_brief.json from full-song MSSL JSON.")
    p.add_argument("--input",required=True); p.add_argument("--output-dir"); p.add_argument("--min-movements",type=int,default=3); p.add_argument("--max-movements",type=int,default=5)
    a=p.parse_args(); src=Path(a.input); profile=json.loads(src.read_text(encoding="utf-8"))
    brief=build(profile,src,a.min_movements,a.max_movements); out=Path(a.output_dir) if a.output_dir else src.parent; out.mkdir(parents=True,exist_ok=True)
    (out/"critical_listening_brief.json").write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"critical_listening_prompt_input.md").write_text(f"{PROMPT}\n\n## MSSL critical listening brief\n\n```json\n{json.dumps(brief,ensure_ascii=False,indent=2)}\n```\n",encoding="utf-8")
    print(f"Wrote {out/'critical_listening_brief.json'}"); print(f"Wrote {out/'critical_listening_prompt_input.md'}")


def build(profile:dict[str,Any],src:Path,min_m:int,max_m:int)->dict[str,Any]:
    raw=profile.get("segments") or profile.get("segment_evidence") or []
    if not isinstance(raw,list) or not raw: raise ValueError("Expected non-empty segments or segment_evidence.")
    cs=[card(s,i) for i,s in enumerate(raw) if isinstance(s,dict)]; sm=summarize(profile,cs); mv=movements(cs,min_m,max_m)
    return {"version":"mssl_critical_listening_brief_v0_1","status":"manual_optional_bridge_not_default_pipeline","source_profile":{"path":str(src),"analysis_label":profile.get("analysis_label"),"source_version":profile.get("version"),"segment_count":len(cs)},"boundary":{"does_not_read_audio":True,"does_not_generate_final_review":True,"does_not_do_asr":True,"does_not_do_singer_identity":True,"does_not_do_instrument_truth":True,"does_not_do_genre_truth":True,"does_not_do_emotion_truth":True},"central_thesis_candidates":theses(sm,mv),"macro_movements":mv,"dominant_listening_objects":objects(cs),"tensions":tensions(sm,mv),"risks_or_limits":risks(profile,sm),"llm_writing_guidance":{"rules":GUIDE}}


def card(s:dict[str,Any],i:int)->dict[str,Any]:
    tr=s.get("time_range") or {}; ome=s.get("ome_mapping") or {}; oc=s.get("object_candidates") or {}; ms=s.get("musical_structure") or {}; midi=s.get("midi_like_skeleton") or {}
    return {"segment_id":str(s.get("segment_id") or f"segment_{i+1:02d}"),"time_label":str(tr.get("label") or f"{clock(num(tr.get('start_seconds')))}-{clock(num(tr.get('end_seconds')))}"),"e":fd(ome.get("e_space_receiver_side") or {}),"obj":fd(oc.get("scores") or {}),"role":str(ms.get("role_label") or "section_like"),"phrase":str(midi.get("phrase_shape") or "unknown")}


def summarize(profile:dict[str,Any],cs:list[dict[str,Any]])->dict[str,Any]:
    roles:dict[str,int]={}
    for c in cs: roles[c["role"]]=roles.get(c["role"],0)+1
    return {"role_counts":roles,"role_diversity":len(roles),"object_means":{k:avg(c["obj"].get(k) for c in cs) for k in OBJ},"e_means":{k:avg(c["e"].get(k) for c in cs) for k in E},"style_status":path(profile,["policy","style_status"]),"mssl_boundary":path(profile,["policy","mssl_boundary"])}


def movements(cs:list[dict[str,Any]],min_m:int,max_m:int)->list[dict[str,Any]]:
    n=len(cs); count=n if n<=3 else min(max_m,max(min_m,3 if n<=10 else 4 if n<=15 else 5),n); prev=None; out=[]
    for i in range(count):
        g=cs[round(i*n/count):round((i+1)*n/count)]; gs=gsummary(g); lab=mlabel(i,count,gs,prev); top=", ".join(x["object"] for x in gs["dominant_objects"][:2])
        out.append({"time_range":span(g),"label":lab,"listening_action":action(lab,top),"supporting_segments":[c["segment_id"] for c in g],"evidence_summary":gs,"confidence":conf(gs,len(g)),"not_proven":["formal verse/chorus truth","producer intent","lyrics-driven interpretation"]}); prev=gs
    return out


def gsummary(g:list[dict[str,Any]])->dict[str,Any]:
    e={k:avg(c["e"].get(k) for c in g) for k in E}; objs={OBJ[k]:avg(c["obj"].get(k) for c in g) for k in OBJ}; roles:dict[str,int]={}; phrases:dict[str,int]={}
    for c in g: roles[c["role"]]=roles.get(c["role"],0)+1; phrases[c["phrase"]]=phrases.get(c["phrase"],0)+1
    return {"field":{"pressure":e["perceived_pressure"],"width":e["perceived_width"],"spread":e["perceived_spread"],"near_far":e["near_far"],"brightness_height":e["high_low"],"envelopment":e["envelopment"]},"dominant_objects":[{"object":n,"mean_support":v} for n,v in sorted(objs.items(),key=lambda x:x[1],reverse=True)[:3]],"section_roles":roles,"phrase_shapes":phrases}


def mlabel(i:int,total:int,gs:dict[str,Any],prev:dict[str,Any]|None)->str:
    f=gs["field"]; pd=f["pressure"]-(prev or {}).get("field",{}).get("pressure",f["pressure"]); wd=f["width"]-(prev or {}).get("field",{}).get("width",f["width"]); top={x["object"]:x["mean_support"] for x in gs["dominant_objects"]}
    if i==0: return "field establishment"
    if i==total-1 and (pd < -0.05 or wd > 0.05): return "release / residual opening"
    if f["pressure"]>0.55 and f["width"]<0.35: return "center compression"
    if wd>0.08: return "spatial re-expansion"
    if top.get("foreground vocal/flow line",0)>=0.50: return "foreground flow concentration"
    if top.get("low-end body",0)>=0.50 or top.get("near rhythmic pulse",0)>=0.45: return "pressure-driven continuation"
    return "field continuation"


def action(label:str,top:str)->str:
    return {"field establishment":f"The opening establishes a listening field around {top}.","center compression":f"The center tightens around {top}; pressure matters more than section contrast.","spatial re-expansion":f"The field opens around {top}, turning width into movement.","foreground flow concentration":f"Attention gathers around {top}; the foreground line carries the argument.","pressure-driven continuation":f"{top} keep propulsion active without a strong formal reset.","release / residual opening":f"The field loosens and leaves {top} as residual carriers."}.get(label,f"The section continues the established field through {top}.")


def objects(cs:list[dict[str,Any]])->list[dict[str,Any]]:
    out=[]
    for k,name in OBJ.items():
        vals=[num(c["obj"].get(k)) for c in cs]; m=avg(vals); pk=max(vals) if vals else 0
        if m<0.30 and pk<0.48: continue
        sup=[c for c in cs if num(c["obj"].get(k))>=max(0.38,m)]
        out.append({"object":name,"role_in_listening":f"{'dominant' if m>=0.55 else 'recurrent' if pk>=0.50 else 'supporting'} listening object; usable as behavior, not identity truth","behavior":behavior(name),"relation_to_other_objects":relation(name),"evidence_support":{"mean_support":m,"peak_support":pk,"supporting_segments":refs(sup[:8])},"not_proven":limits(name)})
    return sorted(out,key=lambda x:x["evidence_support"]["mean_support"],reverse=True)


def behavior(name:str)->str:
    return {"foreground vocal/flow line":"tracks as foreground contour without proving words or performer identity","harmonic / chamber-like surrounding field":"frames the foreground as enclosure rather than decoration only","low-end body":"grounds pressure and body without proving an exact bass instrument","near rhythmic pulse":"organizes forward movement through recurrence and near pressure","texture / edge haze":"softens or roughens object edges"}.get(name,"acts as a bounded listening object")


def relation(name:str)->str:
    return {"foreground vocal/flow line":"can be framed by harmonic field and pressed by body/pulse evidence","harmonic / chamber-like surrounding field":"can surround and scale the foreground line","low-end body":"can pair with rhythmic pulse as body-propulsion support","near rhythmic pulse":"can press against foreground and harmonic layers","texture / edge haze":"can mask object boundaries"}.get(name,"relation remains evidence-limited")


def theses(s:dict[str,Any],mv:list[dict[str,Any]])->list[dict[str,Any]]:
    o=s["object_means"]; e=s["e_means"]; labs={m["label"] for m in mv}; out=[]
    if e["perceived_width"]>=0.30 and ({"center compression","spatial re-expansion"}&labs): out.append(thesis("space acts as propulsion rather than decoration","Pressure/width changes can organize form.",e["perceived_width"],e["perceived_pressure"]))
    if o["object_04_vocal_contour_candidate"]>=0.42 and o["object_03_harmonic_layer"]>=0.42: out.append(thesis("foreground vocal/flow line is framed by a chamber-like harmonic field","Foreground contour and harmonic field recur together.",o["object_04_vocal_contour_candidate"],o["object_03_harmonic_layer"]))
    if {"center compression","spatial re-expansion"}&labs: out.append(thesis("the song works through compression and re-expansion, not chorus-like contrast","The movement map is organized by pressure/width shifts.",0.66,0.70,["formal chorus/verse truth","producer intent"]))
    if o["object_02_low_end_body"]>=0.42 or o["object_01_near_rhythmic_pulse"]>=0.38: out.append(thesis("low-end body and near rhythmic pulse do structural work, not just backing support","Body or pulse support can become critical listening material.",o["object_02_low_end_body"],o["object_01_near_rhythmic_pulse"],["exact bass/drum source","mixing intent"]))
    return out[:4] or [thesis("the song is best approached through object relations rather than raw segment labels","Dominant objects are clearer than formal section truth in this evidence.",0.55,0.55)]


def thesis(t:str,support:str,a:float,b:float,no:list[str]|None=None)->dict[str,Any]: return {"thesis":t,"evidence_support":support,"confidence":round(min(0.88,0.40+avg([a,b])*0.50),4),"not_proven":no or ["taste judgment","genre truth","emotion truth","lyrics or performer identity"]}


def tensions(s:dict[str,Any],mv:list[dict[str,Any]])->list[dict[str,Any]]:
    o=s["object_means"]; e=s["e_means"]; rd=s["role_diversity"]; out=[]
    if o["object_03_harmonic_layer"]>=0.40 and e["perceived_pressure"]>=0.42: out.append(tension("elegant harmonic field vs near-body pressure","Harmonic support and pressure evidence coexist.",o["object_03_harmonic_layer"],e["perceived_pressure"]))
    if o["object_04_vocal_contour_candidate"]>=0.42 and rd<=3: out.append(tension("dense vocal/flow motion vs relatively stable section structure","Foreground contour evidence can remain active while section labels repeat.",0.62,0.70,["actual syllable density","word content","formal section truth"]))
    if e["perceived_width"]>=0.30 and e["perceived_pressure"]>=0.42: out.append(tension("wide stereo environment vs centered foreground compression","Width and pressure are both present as evidence.",e["perceived_width"],e["perceived_pressure"]))
    if any(m["label"]=="pressure-driven continuation" for m in mv) and rd<=3: out.append(tension("propulsive continuity vs weak formal contrast","Pressure/body/pulse can sustain movement even when formal contrast is not strong.",0.58,0.66,["weakness as value judgment","composition intent"]))
    return out[:4]


def tension(t:str,evidence:str,a:float,b:float,no:list[str]|None=None)->dict[str,Any]: return {"tension":t,"evidence_summary":evidence,"confidence":round(min(0.88,0.40+avg([a,b])*0.50),4),"not_proven":no or ["authorial intent","absolute affect truth","exact instrument truth"]}


def risks(profile:dict[str,Any],s:dict[str,Any])->list[str]:
    out=["instrument identity cannot be asserted without stem-backed adapter evidence","emotion words must remain affective tendencies, not truth labels","genre or style words must be style behavior, not authoritative genre truth","lyrics and performer identity cannot be claimed unless supplied by a separate trusted source"]
    if s["role_diversity"]<=3: out.insert(0,"formal section contrast appears weak or repetitive in available heuristic evidence")
    if s.get("style_status"): out.append(f"style status: {s['style_status']}")
    if s.get("mssl_boundary"): out.append(f"MSSL boundary: {s['mssl_boundary']}")
    sep=path(profile,["optional_adapters","source_separation","status"])
    if sep: out.append(f"source separation status: {sep}")
    return out


def limits(name:str)->list[str]: return ["performer identity","word content","isolated stem truth"] if name=="foreground vocal/flow line" else ["exact source identity","authorial intent"]
def conf(gs:dict[str,Any],n:int)->float:
    top=max((x["mean_support"] for x in gs["dominant_objects"]),default=0); f=gs["field"]; return round(min(0.92,0.30+top*0.35+max(f["pressure"],f["width"],f["envelopment"])*0.20+min(n,4)*0.05),4)
def span(g:list[dict[str,Any]])->str: return f"{g[0]['time_label'].split('-')[0]}-{g[-1]['time_label'].split('-')[-1]}"
def refs(cs:list[dict[str,Any]])->list[dict[str,str]]: return [{"segment_id":c["segment_id"],"time_range":c["time_label"]} for c in cs]
def fd(v:Any)->dict[str,float]: return {str(k):num(x) for k,x in v.items() if x is not None} if isinstance(v,dict) else {}
def path(v:dict[str,Any],keys:list[str])->Any:
    cur:Any=v
    for k in keys:
        if not isinstance(cur,dict): return None
        cur=cur.get(k)
    return cur
def avg(values:Any)->float:
    vals=[num(v) for v in values]; return round(sum(vals)/len(vals),4) if vals else 0.0
def num(v:Any)->float:
    try: x=0.0 if v is None else float(v)
    except (TypeError,ValueError): return 0.0
    return x if math.isfinite(x) else 0.0
def clock(sec:float)->str:
    sec=max(0.0,sec); m=int(sec//60); s=int(round(sec-m*60))
    if s>=60: m+=1; s-=60
    return f"{m:02d}:{s:02d}"

if __name__=="__main__": main()
