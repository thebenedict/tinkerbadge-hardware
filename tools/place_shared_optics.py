#!/usr/bin/env python3
"""Stage the joint passive ALS/IR-RX window placement; preserve other circuits."""
from pathlib import Path
import pcbnew as p
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'.build/shared-optics-one-sided'
BASE='a7ac2778f423c3847b9a3a6200f00446d6a960bbee242b6ef8da7aff5ed24b84'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not (R/'~tinkerbadge.kicad_pcb.lck').exists()
assert sha(R/'tinkerbadge.kicad_pcb')==BASE
proposal_path=R/'.build/shared-optics/proposal.json';proposal_hash=sha(proposal_path)
proposal=json.loads(proposal_path.read_text());assert proposal['source_board_sha256']==BASE
for key in ['positive_area_courtyard_collisions','moved_pad_copper_outside_board','moved_pad_keepout_collisions','TX_wall_front_courtyard_hits']:assert not proposal[key],key
assert min(proposal['moved_reference_min_copper_edge_clearance_mm'].values())>=0.5
assert proposal['ALS_glass_courtyard_gap_mm']>=0.5
O.mkdir(parents=True,exist_ok=True)
for name in ['Tinkerbadge.pretty','models']:shutil.copytree(R/name,O/name,dirs_exist_ok=True)
for pattern in ['*.kicad_sch','*.kicad_sym']:
 for f in R.glob(pattern):shutil.copy2(f,O/f.name)
for name in ['tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:shutil.copy2(R/name,O/name)
plan=json.loads((R/'docs/design/pcb_placement.json').read_text())
rows={q['reference']:q for q in plan['placements']+plan['non_electrical_envelopes']}
b=p.LoadBoard(str(R/'tinkerbadge.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
def sig(board):return {f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints()}
before=sig(b);moves=[]
for q in proposal['placements']:
 f=fs[q['reference']];r=rows[q['reference']]
 assert f.GetLayer()==p.F_Cu and q['side']=='F.Cu'
 assert abs(p.ToMM(f.GetPosition().x)-q['original_x'])<1e-5 and abs(p.ToMM(f.GetPosition().y)-q['original_y'])<1e-5
 f.SetOrientationDegrees(q['rotation']);f.SetPosition(p.VECTOR2I(p.FromMM(q['x']),p.FromMM(q['y'])))
 moves.append({'reference':q['reference'],'before':[r['x'],r['y'],r['rotation']],'after':[q['x'],q['y'],q['rotation']]})
 for k in ['x','y','rotation','side']:r[k]=q[k]
plan['status']='shared_passive_optics_and_rear_NFC_plan_pending_human_placement_review'
plan['notes']=[n for n in plan['notes'] if not n.startswith(('Ambient sensing moves left','The complete nine-part IR circuit','Receiver filter/bypass'))]
plan['notes'] += [
 'U501 and its two bypass capacitors now sit beside U504 below the display. The two passive detectors can share a visible-and-940 nm-transmitting window, separate from the IR emitter window and RGB diffuser.',
 'U501 is at (143.5,170.5),90°. Its courtyard clears the glass by 3.655 mm. This improves the display-side view and consolidates the enclosure aperture; it does not improve LED isolation by distance.',
 'R504 moves slightly right to preserve local emitter support and leave an evaluated 0.5 mm-wide enclosure-divider corridor at x146.6..147.1/y165.25..175.75. No enclosure barrier, copper keepout or routing is added.',
 'The lower ALS is about 12.02 mm from its nearest affinity LED. Opaque visible/940 nm barriers, cover transmission/FOV qualification and IR-off integration with LED-on/off characterization remain required.'
]
plan['ir_placement_plan']['ambient_sensor_unchanged']=False
plan['ir_placement_plan']['transmitter_resistor_mm']=[150.75,172,180]
plan['passive_optical_window_plan']={'ALS_mm':[143.5,170.5,90],'IR_receiver_mm':[137.75,168.5,180],'shared_passive_window':True,'separate_IR_transmitter_window':True,'cover':'visible and 940 nm transmitting; characterize spectral response','opaque_isolation_from':['IR transmitter','affinity LED diffuser'],'candidate_TX_divider_corridor_mm':[146.6,165.25,147.1,175.75],'enclosure_implemented':False,'routing_status':'unrouted'}
assert sig(b)==before and len(list(b.GetTracks()))==0 and b.GroupsSanityCheck(False)==''
assert sha(proposal_path)==proposal_hash
b.BuildConnectivity();out=O/'tinkerbadge.kicad_pcb';p.SaveBoard(str(out),b)
check=p.LoadBoard(str(out));assert sig(check)==before and check.GroupsSanityCheck(False)==''
(O/'pcb_placement.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
report={'source_board_sha256':BASE,'board_sha256':sha(out),'proposal_sha256':proposal_hash,'tool':'KiCad '+p.GetBuildVersion(),'moves':moves,'move_count':len(moves),'native_group_count':len(list(check.Groups())),'pad_net_mapping_unchanged':True,'tracks':0,'NFC_geometry_unchanged':True,'status':plan['status']}
(O/'change-report.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(proposal_path,O/'reviewed-proposal.json')
print(json.dumps(report,indent=2))
