#!/usr/bin/env python3
"""Stage the user-approved R2 outline and preserve the published source."""
from pathlib import Path
import pcbnew as p, json, hashlib, math, shutil
R=Path(__file__).resolve().parents[1]
B=R/"tinkerbadge.kicad_pcb"; O=R/".build/routing-pass"
H=R/"docs/design/history/2026-11-10-before-routing"
BASE="ddf824f2a59bc82568bbb03bcb3f89959f2ee12638b380790207739273c1844d"
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(B)==BASE and not (R/"~tinkerbadge.kicad_pcb.lck").exists()
O.mkdir(parents=True,exist_ok=True); H.mkdir(parents=True,exist_ok=True)
sources=["tinkerbadge.kicad_pcb","tinkerbadge.kicad_pro","docs/design/pcb_placement.json","docs/design/pcb_placement_review.md","docs/design/shared_passive_optics_review.md","docs/design/implementation_status.md","exports/tinkerbadge.net"]
for rel in sources:
 dest=H/rel
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert sha(dest)==sha(R/rel)
 else:shutil.copy2(R/rel,dest)
(H/"README.md").write_text("# Published placement before routing\n\nThis preserves the checked, unrouted board and current review records before the authorized R2 tip and routing pass. The complete source and library checkpoint is Git commit 1809844. Board SHA256: "+BASE+". Published viewer snapshot: 9089771cc612. No manufacturing release is implied.\n")
for name in ["Tinkerbadge.pretty","models"]:shutil.copytree(R/name,O/name,dirs_exist_ok=True)
for pattern in ["*.kicad_sch","*.kicad_sym"]:
 for q in R.glob(pattern):shutil.copy2(q,O/q.name)
for name in ["tinkerbadge.kicad_pro","fp-lib-table","sym-lib-table"]:shutil.copy2(R/name,O/name)
b=p.LoadBoard(str(B)); v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
io=p.PCB_IO_KICAD_SEXPR()
def fmt(f):
 io.Format(f);return io.GetStringOutput(True)
before={f.GetReference():fmt(f) for f in b.GetFootprints()}
hits=[]
for d in b.GetDrawings():
 if d.GetLayer()!=p.Edge_Cuts or d.GetShape()!=p.SHAPE_T_SEGMENT:continue
 if d.GetStart()==v(155,106.25) and d.GetEnd()==v(155,100):d.SetEnd(v(155,102));hits.append("wall")
 if d.GetStart()==v(155,100) and d.GetEnd()==v(206,100):d.SetStart(v(157,100));hits.append("top")
assert sorted(hits)==["top","wall"]
arc=p.PCB_SHAPE(b);arc.SetShape(p.SHAPE_T_ARC);arc.SetLayer(p.Edge_Cuts);arc.SetWidth(p.FromMM(.05))
arc.SetArcGeometry(v(155,102),v(157-math.sqrt(2),102-math.sqrt(2)),v(157,100));b.Add(arc)
out=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(out,False,None,False,False)
assert out.OutlineCount()==1 and out.HoleCount(0)==0
assert before=={f.GetReference():fmt(f) for f in b.GetFootprints()}
p.SaveBoard(str(O/"r2-unrouted.kicad_pcb"),b)
p.SaveBoard(str(O/"tinkerbadge.kicad_pcb"),b)
assert p.ExportSpecctraDSN(b,str(O/"inspect.dsn"))
report={"source_commit":"1809844","source_board_sha256":BASE,"staged_board_sha256":sha(O/"tinkerbadge.kicad_pcb"),"tool":p.GetBuildVersion(),"outline_change":"R2 at exposed tip; tangent endpoints (155,102), (157,100), center (157,102). Existing R0.5 concave return retained.","footprints_unchanged":True,"native_outline_valid":True,"routing":False,"active_source_unchanged":sha(B)==BASE}
(O/"r2-change.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

