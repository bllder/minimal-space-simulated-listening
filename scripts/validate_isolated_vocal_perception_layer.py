#!/usr/bin/env python3
"""Synthetic no-song validator for isolated-vocal perceptual proxies."""
from __future__ import annotations
import importlib.util, math, sys, tempfile, wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BUILDER=ROOT/"scripts/build_isolated_vocal_perception_layer.py"

def load_builder():
    spec=importlib.util.spec_from_file_location("ivp",BUILDER)
    if spec is None or spec.loader is None: raise RuntimeError(BUILDER)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m

def tone(sr,dur,a,b,gain,swell=0):
    n=int(sr*dur); f=np.linspace(a,b,n); phase=2*np.pi*np.cumsum(f)/sr; env=np.ones(n); aa=int(.08*sr); rr=int(.18*sr); env[:aa]=np.linspace(0,1,aa); env[-rr:]=np.linspace(1,.02,rr)
    if swell: env*=1+swell*np.sin(np.linspace(0,np.pi,n))
    return (gain*env*(np.sin(phase)+.32*np.sin(2*phase)+.12*np.sin(3*phase))/1.44).astype(np.float32)

def silence(sr,d): return np.zeros(int(sr*d),np.float32)
def write(path,y,sr):
    pcm=(np.clip(y,-1,1)*32767).astype('<i2')
    with wave.open(str(path),'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

def main():
    b=load_builder(); sr=16000
    y=np.concatenate([silence(sr,.8),tone(sr,2.3,220,220,.34),silence(sr,.9),tone(sr,2.8,220,330,.30,.55),silence(sr,.85),tone(sr,2.4,196,208,.25),silence(sr,.8)])
    with tempfile.TemporaryDirectory(prefix='mssl_ivp_') as td:
        p=Path(td)/'synthetic.wav'; write(p,y,sr); x,sr2,meta=b.read_pcm_wav_mono(p)
        d=b.build_layer(x,sr2,meta,'synthetic',-32.0,[b.TimeRange('synthetic_take',0,len(x)/sr2)])
        assert d['status']=='computed_from_local_isolated_vocal_acoustic_proxies'
        assert d['phrase_count']==3,d['phrase_count']
        assert d['human_calibration_interface']['status']=='not_calibrated'
        assert 'infectiousness_or_movingness' in d['unsupported_absolute_judgements']
        p1,p2=d['phrases'][0],d['phrases'][1]
        r1=p1['acoustic_evidence']['pitch_contour']['pitch_range_90_semitones']; r2=p2['acoustic_evidence']['pitch_contour']['pitch_range_90_semitones']
        assert r2>r1+2,(r1,r2)
        assert p2['perceptual_proxy_vector']['pitch_mobility_proxy']['value']>p1['perceptual_proxy_vector']['pitch_mobility_proxy']['value']
        md=b.render_md(d); assert 'What this layer cannot say' in md and 'Truth boundary' in md
    print('isolated-vocal perception validator: PASS')
if __name__=='__main__': main()
