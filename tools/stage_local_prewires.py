#!/usr/bin/env python3
"""Stage explicit local connections and reference-ground fanouts."""
from pathlib import Path
import hashlib,json,pcbnew as p
from pcb_local_routes import Router
R=Path(__file__).resolve().parents[1];O=R/".build/routing-pass"
source=O/"r2-supports-unrouted.kicad_pcb";b=p.LoadBoard(str(source))
constraints=json.loads((R/"docs/design/routing_constraints.json").read_text())
clearances={n:constraints["class_parameters_mm"][c]["clearance"] for n,c in constraints["exact_net_class_assignments"].items()}
r=Router(b,clearances)
# Exact pair endpoints, reviewed native nets. No absent footprint is synthesized.
pairs=[
 ("U104",1,"C112",1,.4),("U104",6,"C114",1,.4),("U104",4,"C113",1,.2),("U104",5,"R119",2,.2),("R119",1,"C114",1,.3),
 ("U107",14,"C115",1,.25),("U107",2,"R128",1,.2),("R127",2,"R128",1,.2),("C116",1,"R128",1,.2),("U107",3,"R130",1,.2),("R130",2,"R129",1,.2),
 ("U506",16,"C514",1,.25),("C514",1,"C515",1,.3),("U301",20,"C312",1,.25),
 ("U501",1,"C501",1,.2),("U501",5,"C502",1,.2),
 ("U502",2,"U502",3,.2),("U502",9,"U502",10,.2),("U502",9,"C503",1,.2),("U502",10,"C504",1,.2),
 ("C503",1,"C505",1,.3),("U503",6,"C506",1,.2),
 ("U504",4,"C510",1,.3),("C510",1,"C509",1,.3),("R507",2,"C510",1,.3),
 ("R504",2,"D501",1,.3),("D501",2,"Q501",3,.3),("R505",2,"Q501",1,.2),("R506",1,"Q501",1,.2),
 ("U201",2,"C202",1,.4),("C202",1,"C201",1,.4),
 ("U102",17,"U102",8,.25),("U102",2,"U102",3,.2),("U102",10,"U102",11,.2),
 ("U102",4,"R120",2,.2),
 ("U502",5,"U502",6,.2),
 ("U505",1,"C511",1,.4),("C512",1,"C511",1,.5),("U505",5,"R508",1,.2),("U505",6,"C513",1,.4),
 ("R118",2,"U103",3,.2),("U103",2,"U103",3,.2),("U103",3,"U103",8,.2),
 ("R117",2,"R118",1,.2),("R117",2,"U103",4,.2),
 ("U103",6,"C108",1,.3),("C108",1,"C109",1,.6),("C107",1,"U103",10,.3),
]
# All eight pixels have a deliberate local supply connection to their own bypass.
for i in range(401,409):pairs.append((f"D{i}",4,f"C{i}",1,.3))
result=[]
# The exposed charger ground pad escapes between its perimeter lands. A
# straight pad-normal route to pin 8 is obstructed by the neighboring power
# land; use this inspected, short in-package dogleg instead of via-in-paste.
ep_path=[(177,124),(177.7,124),(177.7,125.1),(177.75,125.15),(177.75,125.4625)]
assert r.add_path(ep_path,r.pad("U102",17).GetNetCode(),.25)
result.append({"from":"U102.17","to":"U102.8","net":"GND","width_mm":.25,"points_mm":ep_path,"purpose":"EP electrical return; thermal qualification remains open"})
for a,n,c,m,w in pairs:
 if (a,str(n),c,str(m))==("U102","17","U102","8"):continue
 rec=r.connect(a,n,c,m,w)
 if rec:result.append(rec)
# All ground copper is one net. The converter's source-required AGND/PGND
# local topology is held for explicit review rather than generic via placement.
ground=[];failed=[];skipped=[]
for f in b.GetFootprints():
 if f.GetReference() in ["U103","R118"]:
  skipped.append(f.GetReference());continue
 seen=set()
 for pad in f.Pads():
  if pad.GetNetname()!="GND" or not pad.IsOnLayer(p.F_Cu):continue
  # The ESP exposed island includes source-footprint through vias under one pad number.
  if f.GetReference()=="U201" and pad.GetNumber()=="41":
   skipped.append("U201.41 existing footprint thermal via pattern");continue
  if f.GetReference()=="U102" and pad.GetNumber()=="17":continue
  key=(pad.GetNumber(),pad.GetPosition().x,pad.GetPosition().y)
  if key in seen:continue
  seen.add(key)
  width=.2 if min(p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y))<.5 else .3
  rec=r.ground_via(pad,width)
  if rec:ground.append(rec)
  else:failed.append([f.GetReference(),pad.GetNumber()])
rec=r.ground_via(r.pad("U103",8),.25)
assert rec,"Converter PGND via needs explicit review"
ground.append(rec)
b.BuildConnectivity()
out=O/"local-prewired.kicad_pcb";p.SaveBoard(str(out),b)
report={"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"board_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"explicit_connections":result,"failed_connections":r.failures,"ground_fanouts":ground,"failed_ground_fanouts":failed,"held_ground_topology":skipped,"tracks_and_vias":len(list(b.GetTracks())),"status":"Staged only. Native DRC and electrical/visual review required before acceptance."}
(O/"local-prewire-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items()},indent=2))

