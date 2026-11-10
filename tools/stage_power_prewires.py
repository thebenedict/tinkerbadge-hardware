#!/usr/bin/env python3
"""Stage reviewed power-control and short current-path connections."""
from pathlib import Path
import hashlib,json,math,pcbnew as p
from pcb_local_routes import Router
R=Path(__file__).resolve().parents[1];O=R/".build/routing-pass"
src=O/"local-grounded.kicad_pcb";b=p.LoadBoard(str(src));r=Router(b)
result=[];pairs=[
 ("U101",1,"U101",8,.4),("U101",1,"C103",1,.4),("U102",13,"C103",1,.25),
 ("U102",3,"C106",1,.3),("U102",10,"C105",1,.3),("U102",11,"R120",1,.2),
 ("U101",7,"C101",1,.4),("U101",2,"C102",1,.4),
 ("C107",1,"U103",1,.2),
 ("R117",1,"C108",1,.2),
 ("Q301",2,"R301",1,.4),("Q301",1,"R302",1,.2),
]
for a,n,c,m,w in pairs:
 q=r.connect(a,n,c,m,w)
 if q:result.append(q)
names=["MUX_ILM","MUX_SS","MUX_OV_USB","MUX_OV_DOCK","MUX_PRIORITY_USB","CHARGER_ISET","CHARGER_TMR","CHARGER_ILIM"]
for name in names:
 pads=[a for f in b.GetFootprints() for a in f.Pads() if a.GetNumber() and a.GetNetname()=="/01  POWER + CHARGING/"+name]
 components=[{i} for i in range(len(pads))]
 edges=sorted((math.dist((a.GetPosition().x,a.GetPosition().y),(c.GetPosition().x,c.GetPosition().y)),i,j) for i,a in enumerate(pads) for j,c in enumerate(pads) if i<j)
 for distance,i,j in edges:
  left=next(s for s in components if i in s);right=next(s for s in components if j in s)
  if left is right:continue
  a=pads[i];c=pads[j]
  q=r.connect(a.GetParentFootprint().GetReference(),a.GetNumber(),c.GetParentFootprint().GetReference(),c.GetNumber(),.2,max_detour=8)
  if q:
   result.append(q);left.update(right);components.remove(right)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
out=O/"manual-power.kicad_pcb";p.SaveBoard(str(out),b)
report={"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"board_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"connections":result,"failures":r.failures,"tracks_vias":len(list(b.GetTracks())),"status":"Staged routing; DRC and visual checks pending."}
(O/"manual-power-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items()},indent=2))

