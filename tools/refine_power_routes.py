#!/usr/bin/env python3
"""Refine Kelvin, safety-critical local paths and remaining power branches."""
from pathlib import Path
import pcbnew as p,json,hashlib,math
from pcb_local_routes import Router,xy,V
R=Path(__file__).resolve().parents[1];O=R/".build/routing-pass";src=O/"power-distributed.kicad_pcb"
BASE="dedbc611aa42824eb490f9edf9fb8f6d4ff5b77a759246c4f971269e013cdb38"
assert hashlib.sha256(src.read_bytes()).hexdigest()==BASE
b=p.LoadBoard(str(src));removed=[];log=[]
def near(a,c):return math.dist(a,c)<.000003
def remove_path(points,layer,width,net):
 for a,c in zip(points,points[1:]):
  hits=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer()==layer and t.GetNetname()==net and abs(p.ToMM(t.GetWidth())-width)<1e-6 and ((near(xy(t.GetStart()),a) and near(xy(t.GetEnd()),c)) or (near(xy(t.GetEnd()),a) and near(xy(t.GetStart()),c)))]
  assert hits,(a,c,net)
  for t in hits:b.Remove(t);removed.append(t)
pre=json.loads((O/"local-prewire-report.json").read_text())
ce=next(q for q in pre["explicit_connections"] if q.get("from")=="U102.4")
remove_path(ce["points_mm"],p.F_Cu,.2,ce["net"])
sense=next(q for q in json.loads((O/"power-distribution-report.json").read_text())["connections"] if q.get("from")=="C108.1" and q.get("to")=="R117.1")
remove_path(sense["front_stubs_mm"][0],p.F_Cu,.2,"+3V3");remove_path(sense["back_path_mm"],p.B_Cu,.2,"+3V3")
oldvia=next(t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=="+3V3" and near(xy(t.GetPosition()),sense["back_path_mm"][0]))
b.Remove(oldvia);removed.append(oldvia)
spec=json.loads((R/"docs/design/routing_constraints.json").read_text())
clear={n:spec["class_parameters_mm"][c]["clearance"] for n,c in spec["exact_net_class_assignments"].items()}
r=Router(b,clear)
# True capacitor-terminal sensing from an unused portion of its pad edge.
net=r.pad("C108",1).GetNetCode();via=p.PCB_VIA(b);via.SetPosition(V(141.35,151.7));via.SetWidth(p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(net)
assert r.valid(via,.20)
assert r.add_path([(140.175,151.7),(141.35,151.7)],net,.2)
assert r.add_path([(141.35,151.7),(136.774999,147.124999),(136.425,147.124999)],net,.2,p.B_Cu)
b.Add(via);r.register(via)
log.append({"action":"Replace false upstream sense takeoff","new_Kelvin_pad_exit_mm":[140.175,151.7],"new_sense_via_mm":[141.35,151.7],"exception":"Off-center perpendicular exit from unused lower-right capacitor land; no overlap with current feeds outside pad."})
def connected(a,n,c,m):
 b.BuildConnectivity();return r.pad(c,m).m_Uuid.AsString() in {q.m_Uuid.AsString() for q in b.GetConnectivity().GetConnectedItems(r.pad(a,n))}
def attempt(a,n,c,m,width=.2,neck=None):
 if connected(a,n,c,m):return True
 q=r.connect(a,n,c,m,min(width,.6),max_detour=12)
 if not q:q=r.back_connect(a,n,c,m,width,neck or min(width,.3),power=width>=.5)
 if q:log.append(q)
 return bool(q)
# Complete BAT bypass before the low-current CE control route.
assert attempt("U102",3,"C106",1,.3)
assert attempt("U102",4,"R120",2,.2)
for q in [("C105",1,"R120",1,.2),("C105",1,"R110",1,.2),("C105",1,"R111",1,.2),
 ("C104",1,"U101",11,.2),("R105",2,"U101",4,.2),
 ("C109",1,"C512",1,1.0,.5),("C105",1,"C107",1,1.0,.5),
 ("C106",1,"R127",1,.2),("C407",1,"C408",1,.5,.3)]:
 result=attempt(*q)
 if not result:log.append({"remaining":list(q)})
# Extra reference-plane contacts at converter and charger ground current nodes.
for ref,num,viaxy,points in [
 ("U103",8,(140.75,147.85),[(140.65,147),(140.75,147.1),(140.75,147.85)]),
 ("U102",8,(177,126.325),[(177.75,126.325),(177,126.325)])]:
 v=p.PCB_VIA(b);v.SetPosition(V(*viaxy));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(r.pad(ref,num).GetNetCode())
 if r.valid(v) and r.add_path(points,v.GetNetCode(),.3):
  b.Add(v);r.register(v);log.append({"additional_ground_via":ref,"xy_mm":viaxy})
 else:log.append({"ground_reinforcement_pending":ref})
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
out=O/"power-refined.kicad_pcb";p.SaveBoard(str(out),b)
report={"source_sha256":BASE,"board_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"removed_items":len(removed),"actions":log,"tracks_vias":len(list(b.GetTracks()))}
(O/"power-refinement-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items()},indent=2))

