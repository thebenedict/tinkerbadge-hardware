#!/usr/bin/env python3
"""Stage the reviewed top-edge role-light arrangement. No routing or circuit change."""
import pcbnew as p,pathlib,json,hashlib,shutil
R=pathlib.Path(__file__).resolve().parents[1]
S=R/'.build/spread-one-sided';O=R/'.build/top-role-one-sided'
BASE='2ff74d95a154bce47ce87e97cf86c60af26514ff08235ffc70f8b9189b61ddda'
ROOTBASE='a49a19fdf1a2cea1b223f419887e369ab844f49adc9933a0688ba7f01e2ab7b4'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def V(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
assert not (R/'~tinkerbadge.kicad_pcb.lck').exists()
assert sha(R/'tinkerbadge.kicad_pcb')==ROOTBASE
assert sha(S/'tinkerbadge.kicad_pcb')==BASE
proposal_path=R/'.build/top_role_placement_proposal.json';proposal=json.loads(proposal_path.read_text());proposal_hash=sha(proposal_path)
assert proposal['source_board_sha256']==BASE
assert not proposal['positive_area_courtyard_collisions']
assert not proposal['moved_pad_copper_outside_board']
assert not proposal['moved_pad_keepout_collisions']
O.mkdir(parents=True,exist_ok=True)
for name in ['Tinkerbadge.pretty','models']:shutil.copytree(S/name,O/name,dirs_exist_ok=True)
for pattern in ['*.kicad_sch','*.kicad_sym']:
 for f in S.glob(pattern):shutil.copy2(f,O/f.name)
for name in ['tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:shutil.copy2(R/name,O/name)
plan=json.loads((S/'pcb_placement.json').read_text());rows={q['reference']:q for q in plan['placements']+plan['non_electrical_envelopes']}
b=p.LoadBoard(str(S/'tinkerbadge.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
def sig(board):
 return {f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints()}
before=sig(b);moves=[]
for q in proposal['placements']:
 f=fs[q['reference']];r=rows[q['reference']]
 assert f.GetLayer()==p.F_Cu and q['side']=='F.Cu'
 assert abs(p.ToMM(f.GetPosition().x)-q['original_x'])<.00001
 assert abs(p.ToMM(f.GetPosition().y)-q['original_y'])<.00001
 f.SetOrientationDegrees(q['rotation']);f.SetPosition(V(q['x'],q['y']))
 moves.append({'reference':q['reference'],'before':[r['x'],r['y'],r['rotation']],'after':[q['x'],q['y'],q['rotation']]})
 for k in ['x','y','rotation','side']:r[k]=q[k]
groups={g.GetName():g for g in b.Groups()}
ambient=groups['Ambient-light bypass'];ambient.SetName('Ambient-light sensor');ambient.AddItem(fs['U501'])
for spec in proposal['groups']:
 if spec['name']=='Ambient-light sensor':g=ambient
 else:
  g=p.PCB_GROUP(b);g.SetName(spec['name']);b.Add(g)
  for ref in spec['references']:g.AddItem(fs[ref])
 for ref in spec['references']:rows[ref]['group']=spec['name']
assert b.GroupsSanityCheck(False)==''
plan['native_functional_groups']=[{'name':g.GetName(),'references':sorted(p.Cast_to_FOOTPRINT(i).GetReference() for i in g.GetItems())} for g in b.Groups()]
plan['status']='organized_80mm_top_role_row_pending_human_review_and_RF_qualification'
plan['top_role_row']={'centers_x_mm':[160,180.5,201],'center_y_mm':103,'pitch_mm':20.5,'straight_top_edge_x_mm':[155,206],'end_center_margins_mm':[5,5],'LED_rotation_degrees':180}
plan['notes']+=['Latest user instruction supersedes prior role-light locations: all three role LEDs are evenly spaced along the remaining straight top edge, with 5 mm center margins.',
'IR and ambient sensing moved to clear the role row; the receiver remains outside the raised glass. Receiver filter/bypass positions were refined close to its actual supply pins.',
'Labels requested for the review render are separate overlays, not copper or silkscreen modifications.']
assert sig(b)==before and len(list(b.GetTracks()))==0
assert sha(proposal_path)==proposal_hash
b.BuildConnectivity();out=O/'tinkerbadge.kicad_pcb';p.SaveBoard(str(out),b)
check=p.LoadBoard(str(out));assert sig(check)==before
assert check.GroupsSanityCheck(False)==''
plan['notes']=['Experimental 110 × 80 mm placement. Human approval is required before routing; no routing has been performed.', 'All 164 non-test electrical footprints are front-side, including two tuning footprints marked DNP in custom fields. Six bare copper test pads remain on the rear. The proposed rear through-hole SAO socket would require secondary assembly.', 'The proposed panel underside is 4.5 mm above the front PCB surface, with a 0.92 mm glass envelope. Supports, solder/warp/tolerance stack and flex remain unqualified.', 'The full native module keepout remains on all four copper layers, and the left-open board cutout removes FR4 beneath it. Glass is only 3.5 mm behind the antenna, below the recommended 15 mm surrounding clearance. RF performance remains unqualified.', 'The 18 × 13 mm NFC reserve replaces the prior 30 × 17 mm reserve. No coil copper exists; inductance, coupling, read range and tuning remain open.', 'The five bottom LEDs have 23.5 mm pitch from x 108 to 202, all y 174. The leftmost X remains 108; the row moved up for the compact board.', 'The three role LEDs are evenly spaced at x 160, 180.5 and 201, all y 103. Their 20.5 mm pitch and 5 mm end-center margins follow the latest user request and supersede prior role-LED positions.', 'Textile cord reservations have Ø5.2 mm sweep and Ø3.2 mm drills; no metal clip is qualified. Structural holes are Ø2.2 mm with a maximum Ø4.5 mm nonconductive head/boss assumption.', 'The existing USB hole-to-pad DRC failures remain unresolved. Nine electrical footprints remain unassigned. Charging is disabled.', 'The user requested organized circuit groups spread into available board area and removal of the narrow PCB sliver left of the antenna opening.', 'Rigid moves preserve the local geometry of ADC sensing, converter, display power switch and I/O expander. The longer VSYS feed needs low-impedance copper and a continuous return.', 'Sensor bypass placement follows the source contract: C501/C502 at U501, and C503/C504/C505 at U502. Values, nets and selected footprints are unchanged.', 'IR and ambient sensing move clear of the top LED row. The receiver remains outside the raised glass, and its filter/bypass components sit close to the actual supply pins. Optical isolation remains to be qualified.', 'The requested functional-block labels are separate render overlays, with no copper or silkscreen changes.', 'All RF, display-flex, exact-part, manufacturing and human placement-review gates remain in force.']
plan['blocked_electrical_references']['L101']='exact 0.47 µH inductor'
plan['blocked_electrical_references']['L301']='exact 68 µH inductor'
(O/'pcb_placement.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
report={'source_board_sha256':BASE,'root_before_sha256':ROOTBASE,'board_sha256':sha(out),'proposal_sha256':proposal_hash,'tool':'KiCad '+p.GetBuildVersion(),'moves':moves,'move_count':len(moves),'native_group_count':len(list(check.Groups())),'pad_net_mapping_unchanged':True,'tracks':0,'status':plan['status']}
(O/'change-report.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2(proposal_path,O/'reviewed-proposal.json')
print(json.dumps({k:v for k,v in report.items() if k!='moves'},indent=2))

