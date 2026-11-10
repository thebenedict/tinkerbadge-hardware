#!/usr/bin/env python3
"""Add independently checked return stitches to an isolated routing candidate.

The native source, its paired project and the active project remain untouched.
Use tools/run_pcb_native.sh with the installed KiCad Python.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
import pcbnew as p
from pcb_local_routes import Router,V

def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def fmt(item):
    io=p.PCB_IO_KICAD_SEXPR();io.Format(item);return io.GetStringOutput(True)
ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('source_sha');ap.add_argument('stitches',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
assert sha(a.source)==a.source_sha
sourcepro=a.source.with_suffix('.kicad_pro');assert sourcepro.exists();prosha=sha(sourcepro)
a.output.parent.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(a.source));original={t.m_Uuid.AsString():fmt(t) for t in b.GetTracks()};fp_before={f.m_Uuid.AsString():fmt(f) for f in b.GetFootprints()}
spec=json.load(open(Path(__file__).resolve().parents[1]/'docs/design/routing_constraints.json'))
clear={n:spec['class_parameters_mm'][c]['clearance'] for n,c in spec['exact_net_class_assignments'].items()};r=Router(b,clear)
plan=json.loads(a.stitches.read_text());ground=b.FindNet('GND');assert ground and len(plan['points'])>0
added=[]
for x,y in plan['points']:
    v=p.PCB_VIA(b);v.SetPosition(V(x,y));v.SetWidth(p.FromMM(plan['via_diameter_mm']));v.SetDrill(p.FromMM(plan['via_drill_mm']));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(ground.GetNetCode())
    assert r.valid(v),('Return stitch obstructed in final source',x,y)
    b.Add(v);r.register(v);added.append(v)
label='EXPERIMENTAL 110 x 80 - UNROUTED - HUMAN REVIEW REQUIRED';found=0
for d in b.GetDrawings():
    if isinstance(d,p.PCB_TEXT) and d.GetText()==label:
        d.SetText('EXPERIMENTAL 110 x 80 - FIRST ROUTING PASS - REVIEW REQUIRED');found+=1
assert found==1
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
planes=[z for z in b.Zones() if not z.GetIsRuleArea()];assert len(planes)==2
returnchecks=[]
for v in added:
    row=[]
    for z in planes:
        q=z.GetFilledPolysList(z.GetLayer());row.append(q.Contains(v.GetPosition()))
    assert all(row),('Return via lacks filled ground',v.GetPosition(),row)
    returnchecks.append({'x_mm':p.ToMM(v.GetPosition().x),'y_mm':p.ToMM(v.GetPosition().y),'uuid':v.m_Uuid.AsString(),'both_GND_planes':all(row)})
assert original=={t.m_Uuid.AsString():fmt(t) for t in b.GetTracks() if t.m_Uuid.AsString() in original}
assert fp_before=={f.m_Uuid.AsString():fmt(f) for f in b.GetFootprints()}
p.SaveBoard(str(a.output),b);shutil.copy2(sourcepro,a.output.with_suffix('.kicad_pro'))
assert sha(a.source)==a.source_sha and sha(sourcepro)==prosha
(a.output.parent/'final-stitch-report.json').write_text(json.dumps({'source_board_sha256':a.source_sha,'final_board_sha256':sha(a.output),'project_sha256':prosha,'preserved_copper_items':len(original),'added_ground_vias':len(added),'stitches':returnchecks,'footprints_unchanged':True,'outside_board_label_updated':True,'zones_refilled':True,'drc_status':'Run native final DRC separately.'},indent=2)+'\n')
print(sha(a.output))
