#!/usr/bin/env python3
"""Stage deliberate distribution branches over the two GND references."""
from pathlib import Path
import pcbnew as p,json,hashlib,math
from pcb_local_routes import Router,xy
R=Path(__file__).resolve().parents[1];O=R/".build/routing-pass";src=O/"manual-power.kicad_pcb"
b=p.LoadBoard(str(src));r=Router(b);done=[];fail=[]
def linked(a,n,c,m):
 b.BuildConnectivity();ids={q.m_Uuid.AsString() for q in b.GetConnectivity().GetConnectedItems(r.pad(a,n))}
 return r.pad(c,m).m_Uuid.AsString() in ids
def route(a,n,c,m,w,neck=None,back=False):
 if linked(a,n,c,m):return
 q=None if back else r.connect(a,n,c,m,min(w,.6),max_detour=10)
 if q is None:q=r.back_connect(a,n,c,m,w,neck or min(w,.3),power=w>=.5)
 if q:done.append(q)
 else:fail.append([a,n,c,m,w])
# Quiet feedback samples the first output capacitor, never a distant load branch.
route("C108",1,"R117",1,.2)
# Main distribution topology. Long power branches use back copper referenced to In2.
for args in [
 ("C108",1,"C201",1,1.0,.5,True),("C109",1,"C512",1,1.0,.5,True),
 ("C109",1,"C112",1,.6,.4,False),("C108",1,"C514",1,.5,.3,True),
 ("C108",1,"C115",1,.3,.25,True),("C514",1,"C503",1,.4,.25,False),
 ("C512",1,"C506",1,.3,.25,False),("C514",1,"C409",1,.6,.4,True),
 ("C409",1,"C401",1,.5,.3,True),("C401",1,"C402",1,.5,.3,True),("C402",1,"C403",1,.5,.3,True),
 ("C109",1,"C404",1,.5,.3,True),("C404",1,"C405",1,.5,.3,True),("C405",1,"C406",1,.5,.3,True),
 ("C406",1,"C407",1,.5,.3,True),("C407",1,"C408",1,.5,.3,True),
 ("C405",1,"C501",1,.3,.25,False),("C501",1,"C502",1,.3,.2,False),
 ("C406",1,"R504",1,.3,.25,False),("C505",1,"U502",2,.2,.2,False),
 ("C115",1,"U107",1,.2,.2,False),
 ("C105",1,"C107",1,1.0,.5,True),
 ("C106",1,"R127",1,.2,.2,True),
 ("R130",2,"U201",39,.2,.2,True),
 ("C114",1,"C312",1,.6,.3,True),
 ("C513",1,"R507",1,.3,.25,True)
]:route(*args)
# Small +3V3 bias loads branch from nearby local supply nodes. Never use the
# converter FB resistor as a distribution endpoint.
bias=["R116","R510","R123","R414","R501","R305","R503","R126","R502","R202","R201","R412","R115"]
anchors=["C201","C409","C401","C402","C403","C404","C405","C406","C407","C408","C514","C115","C503","C506","C512","C501"]
for ref in bias:
 pads=[a for a in r.fs[ref].Pads() if a.GetNetname()=="+3V3"];assert len(pads)==1
 pad=pads[0]
 targets=sorted(anchors,key=lambda s:math.dist(xy(pad.GetPosition()),xy(r.pad(s,1).GetPosition())))
 for target in targets[:4]:
  before=len(done);route(ref,pad.GetNumber(),target,1,.2,.2,False)
  if linked(ref,pad.GetNumber(),target,1):break
# Ground edge pin that cannot take a straight via fanout near NFC lands.
# It still receives a local plane connection, never NFC antenna copper.
rec=r.ground_via(r.pad("U503",2),.15)
if rec:done.append({"ground_fanout":rec})
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
out=O/"power-distributed.kicad_pcb";p.SaveBoard(str(out),b)
report={"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"board_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"connections":done,"failed_attempts":fail,"tracks_vias":len(list(b.GetTracks())),"status":"Staged provisional routing; final DRC, return paths, power via reinforcement and visuals pending."}
(O/"power-distribution-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items()},indent=2))

