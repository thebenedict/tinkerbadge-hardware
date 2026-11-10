#!/usr/bin/env python3
"""Check a routing candidate against the published electrical/placement source."""
from pathlib import Path
import sys,json,hashlib,re,collections
import pcbnew as p
R=Path(__file__).resolve().parents[1];candidate=Path(sys.argv[1]).resolve()
base=R/"docs/design/history/2026-11-10-before-routing/tinkerbadge.kicad_pcb"
assert hashlib.sha256(base.read_bytes()).hexdigest()=="ddf824f2a59bc82568bbb03bcb3f89959f2ee12638b380790207739273c1844d"
old=p.LoadBoard(str(base));b=p.LoadBoard(str(candidate))
def parse(s):
 tokens=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',s);stack=[];out=[]
 for t in tokens:
  if t=="(":
   x=[]
   if stack:stack[-1].append(x)
   else:out.append(x)
   stack.append(x)
  elif t==")":stack.pop()
  else:stack[-1].append(t)
 assert not stack and len(out)==1
 return out[0]
def canon(x):
 if not isinstance(x,list):return ("atom",x)
 if x and x[0] in ["pts","members"]:return ("ordered",tuple(canon(y) for y in x))
 return ("expr",tuple(y for y in x if not isinstance(y,list)),tuple(sorted(canon(y) for y in x if isinstance(y,list))))
def fmt(f):
 io=p.PCB_IO_KICAD_SEXPR();io.Format(f);return canon(parse(io.GetStringOutput(True)))
ofs={f.GetReference():f for f in old.GetFootprints()};fs={f.GetReference():f for f in b.GetFootprints()}
assert set(ofs)==set(fs)
expected={"C202":(118.5,108.8,180),"C511":(193,154.65,90),"C512":(193.8,151.3,90),"R508":(197.925,158.3,270)}
pose=lambda f:(p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()%360)
moves=sorted(r for r in fs if pose(fs[r])!=pose(ofs[r]))
assert moves==sorted(expected),moves
for r,pos in expected.items():assert pose(fs[r])==pos,(r,pose(fs[r]),pos)
check=p.LoadBoard(str(candidate));errors=[]
for f in check.GetFootprints():
 o=ofs[f.GetReference()];f.SetOrientationDegrees(o.GetOrientationDegrees());f.SetPosition(o.GetPosition())
 if fmt(f)!=fmt(o):errors.append(f.GetReference())
assert not errors,errors
signature=lambda board:{f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints()}
assert signature(old)==signature(b)
def intersect(a,c):
 if not a.OutlineCount() or not c.OutlineCount() or not a.BBox().Intersects(c.BBox()):return 0
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(a,c);return q.Area()/1e12
outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline,False,None,False,False)
assert outline.OutlineCount()==1 and outline.HoleCount(0)==0
keeps=[z for f in b.GetFootprints() for z in f.Zones() if z.GetIsRuleArea()]+[z for z in b.Zones() if z.GetIsRuleArea()]
paste=[]
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
  for side,pastelayer in [(p.F_Cu,p.F_Paste),(p.B_Cu,p.B_Paste)]:
   if not a.IsOnLayer(pastelayer):continue
   q=p.SHAPE_POLY_SET();a.TransformShapeToPolygon(q,side,0,p.FromMM(.001),p.ERROR_OUTSIDE)
   paste.append((f.GetReference(),a.GetNumber(),side,q))
blocked=[];outside=[];via_paste=[];nc=[];counts=collections.Counter();widths=collections.Counter()
for t in b.GetTracks():
 via=isinstance(t,p.PCB_VIA);counts["vias" if via else "tracks"]+=1
 if t.GetNetname().startswith("unconnected-"):nc.append(t.m_Uuid.AsString())
 layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu] if via else [t.GetLayer()]
 if not via:widths[(b.GetLayerName(t.GetLayer()),round(p.ToMM(t.GetWidth()),4))]+=1
 for layer in layers:
  q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,layer,0,p.FromMM(.001),p.ERROR_OUTSIDE)
  delta=p.SHAPE_POLY_SET();delta.BooleanSubtract(q,outline)
  if delta.Area()>0:outside.append(t.m_Uuid.AsString())
  for z in keeps:
   if z.IsOnLayer(layer) and intersect(q,z.Outline())>0:blocked.append(t.m_Uuid.AsString())
  if via:
   for ref,num,side,poly in paste:
    if side==layer and intersect(q,poly)>0:via_paste.append([t.m_Uuid.AsString(),ref,num])
assert not blocked and not outside and not nc
b.BuildConnectivity()
def connected(a,n,c,m):
 pa=next(q for q in fs[a].Pads() if q.GetNumber()==str(n));pc=next(q for q in fs[c].Pads() if q.GetNumber()==str(m))
 return pc.m_Uuid.AsString() in {q.m_Uuid.AsString() for q in b.GetConnectivity().GetConnectedItems(pa)}
critical={"charger_CE_tied_to_VSYS":connected("R120",1,"U102",10) and connected("R120",2,"U102",4),"BAT_local_bypass":connected("C106",1,"U102",2) and connected("C106",1,"U102",3),"charger_EP_ground":connected("U102",17,"U102",8),"converter_control_ground_local":connected("R118",2,"U103",3) and connected("U103",3,"U103",8)}
assert all(critical.values()),critical
planes=[z for z in b.Zones() if not z.GetIsRuleArea()]
assert len(planes)==2 and {z.GetLayer() for z in planes}=={p.In1_Cu,p.In2_Cu} and all(z.GetNetname()=="GND" for z in planes)
report={"source_sha256":hashlib.sha256(base.read_bytes()).hexdigest(),"candidate_sha256":hashlib.sha256(candidate.read_bytes()).hexdigest(),"tool":p.GetBuildVersion(),"footprint_count":len(fs),"poses_changed":moves,"complete_inverse_footprint_differences":errors,"pad_net_mapping_unchanged":True,"outline_valid":True,"outline_primitives":sum(d.GetLayer()==p.Edge_Cuts for d in b.GetDrawings()),"counts":dict(counts),"widths":[{"layer":l,"width_mm":w,"count":v} for (l,w),v in sorted(widths.items())],"copper_outside":outside,"copper_keepout_intersections":blocked,"NC_net_copper":nc,"new_via_SMD_land_intersections":via_paste,"critical_local_connections":critical,"plane_layers":[b.GetLayerName(z.GetLayer()) for z in planes],"status":"Native geometry/electrical-delta check; DRC, return-path and visual review are separate."}
out=candidate.parent/"routing-delta-check.json";out.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2))
assert not via_paste,via_paste

