#!/usr/bin/env python3
"""Build human A/B calibration packets from isolated-vocal proxy output."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def read(path): return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--input",required=True); parser.add_argument("--output",default=None); args=parser.parse_args()
    data=read(args.input); takes=data.get("take_summaries") or []
    if len(takes)<2: raise SystemExit("Need at least two take summaries for pairwise calibration.")
    phrases=data.get("phrases") or []; packets=[]
    for i in range(len(takes)-1):
        for j in range(i+1,len(takes)):
            a,b=takes[i],takes[j]; av=a.get("aggregate_proxy_vector",{}); bv=b.get("aggregate_proxy_vector",{}); deltas={}
            for key in sorted(set(av)&set(bv)):
                x=float(av[key]["value"]); y=float(bv[key]["value"])
                deltas[key]={"a":x,"b":y,"b_minus_a":round(y-x,6),"boundary":"Proxy difference only; not a preference verdict."}
            pa=[p for p in phrases if p.get("take_id")==a["take_id"]]; pb=[p for p in phrases if p.get("take_id")==b["take_id"]]
            aligned=[{"pair_index":n,"a":{"phrase_id":x["phrase_id"],"start":x["start"],"end":x["end"]},"b":{"phrase_id":y["phrase_id"],"start":y["start"],"end":y["end"]},"alignment_status":"sequence_order_only_not_lyric_verified"} for n,(x,y) in enumerate(zip(pa,pb),1)]
            packets.append({"pair_id":f"{a['take_id']}__vs__{b['take_id']}","take_a":a["take_id"],"take_b":b["take_id"],"proxy_deltas":deltas,"sequence_phrase_pairs":aligned,"human_label_form":{"naturalness":"A|B|tie|unsure","engagement":"A|B|tie|unsure","intentionality":"A|B|tie|unsure","timbre_preference":"A|B|tie|unsure","overall_preference":"A|B|tie|unsure","note":"free text"},"truth_boundary":"No winner is inferred before a human label is attached."})
    output={"version":"vocal_pairwise_calibration_packet_v0_1","status":"ready_for_human_ab_labels","source_layer_version":data.get("version"),"pair_count":len(packets),"pairs":packets,"future_use":"Accumulate pairwise labels, then fit listener-specific or panel preference probability over MSSL vocal evidence/proxy vectors."}
    path=Path(args.output) if args.output else Path(args.input).with_name("vocal_pairwise_calibration_packet.json"); path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8"); print(f"Wrote {path}")
if __name__=="__main__": main()
