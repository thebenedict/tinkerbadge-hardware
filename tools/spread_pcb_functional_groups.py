#!/usr/bin/env python3
"""Stage the requested organized placement and left-open antenna shoulder.
Reads a reviewed proposal, preserves the previous native checkpoint, never routes.
"""
import pcbnew as p, pathlib, json, hashlib, shutil, copy
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='a49a19fdf1a2cea1b223f419887e369ab844f49adc9933a0688ba7f01e2ab7b4'
BOARD=ROOT/'tinkerbadge.kicad_pcb'
STAGE=ROOT/'.build/spread-one-sided'
HIST=ROOT/'docs/design/history/2026-11-09-80mm-before-group-spacing'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def V(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
assert not (ROOT/'~tinkerbadge.kicad_pcb.lck').exists()
assert sha(BOARD)==BASE,'Active board changed; review before rebuilding.'
proposal=json.loads((ROOT/'.build/spread_groups_proposal.json').read_text())
assert proposal['source_board_sha256']==BASE
assert not proposal['positive_area_courtyard_collisions']
plan=json.loads((ROOT/'docs/design/pcb_placement.json').read_text())
if not HIST.exists():
 HIST.mkdir(parents=True)
 for pattern in ['*.kicad_sch','*.kicad_sym']:
  for f in ROOT.glob(pattern):shutil.copy2(f,HIST/f.name)
 for name in ['tinkerbadge.kicad_pcb','tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:
  shutil.copy2(ROOT/name,HIST/name)
 for name in ['Tinkerbadge.pretty','models']:shutil.copytree(ROOT/name,HIST/name)
 for src,dst in [('docs/design/pcb_placement.json','pcb_placement.json'),('docs/design/pcb_placement_review.md','pcb_placement_review.md'),('exports/pcb-review/checkpoint-manifest.json','checkpoint-manifest.json'),('exports/tinkerbadge.net','tinkerbadge.net')]:
  shutil.copy2(ROOT/src,HIST/dst)
 shutil.copytree(ROOT/'exports/pcb-review/compact-one-sided',HIST/'review-artifacts')
 (HIST/'README.md').write_text('# Preserved compact placement before group spacing\n\nBoard SHA256 '+BASE+'. This is the first checked 110 x 80 mm front-SMT experiment. It retains the former left PCB sliver and earlier sensor capacitor placement allocation. It is historical, unrouted, and not a manufacturing release.\n')
STAGE.mkdir(parents=True,exist_ok=True)
for name in ['Tinkerbadge.pretty','models']:shutil.copytree(ROOT/name,STAGE/name,dirs_exist_ok=True)
for pattern in ['*.kicad_sch','*.kicad_sym']:
 for f in ROOT.glob(pattern):shutil.copy2(f,STAGE/f.name)
for name in ['tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:shutil.copy2(ROOT/name,STAGE/name)
b=p.LoadBoard(str(BOARD));fs={f.GetReference():f for f in b.GetFootprints()}
rows={q['reference']:q for q in plan['placements']+plan['non_electrical_envelopes']}
def electrical_signature(board):
 return {f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints() if not f.GetReference().startswith(('MECH_','RES_','H'))}
before=electrical_signature(b)
moves=[]
for q in proposal['placements']:
 f=fs[q['reference']];r=rows[q['reference']]
 assert q['side']=='F.Cu' and f.GetLayer()==p.F_Cu
 assert abs(p.ToMM(f.GetPosition().x)-q['original_x'])<.00001
 assert abs(p.ToMM(f.GetPosition().y)-q['original_y'])<.00001
 f.SetOrientationDegrees(q['rotation']);f.SetPosition(V(q['x'],q['y']))
 moves.append({'reference':q['reference'],'before':[r['x'],r['y'],r['rotation']],'after':[q['x'],q['y'],q['rotation']]})
 for k in ['x','y','rotation','side','group']:r[k]=q[k]
# Make complete functional sets selectable as groups in the native editor.
assert len(list(b.Groups()))==0
for spec in proposal['groups']:
 group=p.PCB_GROUP(b);group.SetName(spec['name']);b.Add(group)
 for ref in spec['references']:group.AddItem(fs[ref])
 for ref in spec['references']:
  if ref in rows:rows[ref]['group']=spec['name']
assert b.GroupsSanityCheck(False)==''
# Correct stale semantic grouping for the already-local mux bypass capacitors.
rows['C101']['group']='Power mux input bypass'
rows['C102']['group']='Power mux input bypass'
# Keep removed native objects alive until process exit (KiCad object-lifetime quirk).
removed=[]
for d in list(b.GetDrawings()):
 if d.GetLayer()==p.Edge_Cuts:
  b.Remove(d);removed.append(d)
def seg(a,c):
 d=p.PCB_SHAPE(b);d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(V(*a));d.SetEnd(V(*c));d.SetLayer(p.Edge_Cuts);d.SetWidth(p.FromMM(.05));b.Add(d)
def arc(a,m,c):
 d=p.PCB_SHAPE(b);d.SetShape(p.SHAPE_T_ARC);d.SetArcGeometry(V(*a),V(*m),V(*c));d.SetLayer(p.Edge_Cuts);d.SetWidth(p.FromMM(.05));b.Add(d)
arc((100,110.75),(101.171572875,107.921572875),(104,106.75))
seg((104,106.75),(154.5,106.75))
arc((154.5,106.75),(154.853553391,106.603553391),(155,106.25))
seg((155,106.25),(155,100));seg((155,100),(206,100))
arc((206,100),(208.828427125,101.171572875),(210,104));seg((210,104),(210,176))
arc((210,176),(208.828427125,178.828427125),(206,180));seg((206,180),(104,180))
arc((104,180),(101.171572875,178.828427125),(100,176));seg((100,176),(100,110.75))
labels={
'EXPERIMENTAL110x80 - UNROUTED - HUMAN REVIEW REQUIRED':'EXPERIMENTAL 110 x 80 - UNROUTED - HUMAN REVIEW REQUIRED',
'Front SMT / display underside4.5mm proposed / RF and flex unqualified':'Front SMT / organized groups / display underside 4.5 mm proposed',
'NOTCH removes FR4; display does NOT meet15mm antenna clearance':'LEFT-OPEN ANTENNA SHOULDER / glass does not meet 15 mm RF clearance',
'NFC18x13 RESERVE':'NFC 18 x 13 RESERVE'
}
for d in b.GetDrawings():
 if isinstance(d,p.PCB_TEXT) and d.GetText() in labels:d.SetText(labels[d.GetText()])
plan['status']='organized_80mm_one_sided_placement_pending_human_review_and_RF_qualification'
plan['outline_note']='Antenna cutout is open to the left edge. Outer R4 from (100,110.75) to (104,106.75); shoulder to (154.5,106.75), inner R0.5 return to (155,106.25), then top edge at y100. Overall 110 x 80 mm.'
plan['native_functional_groups']=[{'name':s['name'],'references':s['references']} for s in proposal['groups']]
plan['notes']+=['User requested organized groups spread into the available area and removal of the thin PCB sliver left of the antenna notch.',
'Rigid functional moves preserve local geometry of the ADC, converter, display power switch and I/O expander. The longer VSYS feed needs low-impedance copper and continuous return.',
'Sensor bypass placement was corrected from the source contract: C501/C502 at U501; C503/C504/C505 at U502. Values, nets and selected footprints are unchanged.',
'No routing. All previous RF, display flex, exact-part and manufacturing gates remain in force.']
assert electrical_signature(b)==before
assert len(list(b.GetTracks()))==0
assert sha(BOARD)==BASE
b.BuildConnectivity();out=STAGE/'tinkerbadge.kicad_pcb';p.SaveBoard(str(out),b)
check=p.LoadBoard(str(out));assert electrical_signature(check)==before
assert check.GroupsSanityCheck(False)==''
(STAGE/'pcb_placement.json').write_text(json.dumps(plan,indent=2)+'\n')
report={'source_sha256':BASE,'board_sha256':sha(out),'status':plan['status'],'tool':'KiCad '+p.GetBuildVersion(),'moved_references':moves,'move_count':len(moves),'functional_groups':plan['native_functional_groups'],'electrical_pad_net_mapping_unchanged':True,'tracks':0,'remaining':'Native DRC, independent final readback, visual review and human placement approval. RF/flex/part-selection gates remain.'}
(STAGE/'change-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['moved_references','functional_groups']},indent=2))

