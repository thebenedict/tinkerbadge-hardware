#!/usr/bin/env python3
"""Stage the independently reviewed local support corrections."""
from pathlib import Path
import json,hashlib,pcbnew as p
R=Path(__file__).resolve().parents[1];O=R/".build/routing-pass"
src=O/"r2-unrouted.kicad_pcb";b=p.LoadBoard(str(src));fs={f.GetReference():f for f in b.GetFootprints()}
moves={"C511":(193,154.65,90),"C512":(193.8,151.3,90),"R508":(197.925,158.3,270),"C202":(118.5,108.8,180)}
changes=[]
for ref,(x,y,a) in moves.items():
 f=fs[ref];old=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()]
 if ref=="C202":assert old[:2]==[x,y],old
 f.SetOrientationDegrees(a);f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
 changes.append({"reference":ref,"before":old,"after":[x,y,a]})
courts={}
for ref,f in fs.items():
 f.BuildCourtyardCaches();q=f.GetCourtyard(p.F_Cu)
 if q.OutlineCount():courts[ref]=q
collisions=[]
for ref in moves:
 for other,q in courts.items():
  if other==ref:continue
  hit=p.SHAPE_POLY_SET();hit.BooleanIntersection(courts[ref],q)
  if hit.Area()>0:collisions.append([ref,other,hit.Area()/1e12])
assert not collisions,collisions
outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline,False,None,False,False)
outside=[]
for ref in moves:
 for pad in fs[ref].Pads():
  q=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(q,p.F_Cu,0,p.FromMM(.001),p.ERROR_OUTSIDE)
  diff=p.SHAPE_POLY_SET();diff.BooleanSubtract(q,outline)
  if diff.Area()>0:outside.append([ref,pad.GetNumber()])
assert not outside
out=O/"r2-supports-unrouted.kicad_pcb";p.SaveBoard(str(out),b)
(O/"support-corrections.json").write_text(json.dumps({"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"board_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"moves":changes,"positive_area_courtyard_collisions":collisions,"copper_outside":outside,"authorization":"Authorized routing includes narrow local support corrections that preserve visible mechanical and user-interface anchors."},indent=2)+"\n")
print("Four support corrections staged; native courtyard and on-board pad checks pass.")

