#!/usr/bin/env python3
"""Stage the user-requested lower IR group; preserve every other circuit."""
import pcbnew as p
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'.build/lower-ir-one-sided'
BASE='8fa1ac386d237944d634cd7b5be0ca3ad3188f87965fbee94499eb1a51859399'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert not (R/'~tinkerbadge.kicad_pcb.lck').exists()
assert sha(R/'tinkerbadge.kicad_pcb')==BASE
proposal_path=R/'.build/lower_ir_proposal.json';proposal_hash=sha(proposal_path)
proposal=json.loads(proposal_path.read_text());assert proposal['source_board_sha256']==BASE
for key in ['positive_area_courtyard_collisions','moved_pad_copper_outside_board','moved_pad_keepout_collisions']:
    assert not proposal[key],key
assert min(proposal['moved_reference_min_copper_edge_clearance_mm'].values())>=0.5
assert min(proposal['optical_courtyard_to_glass_mm'].values())>=0.5
O.mkdir(parents=True,exist_ok=True)
for name in ['Tinkerbadge.pretty','models']:shutil.copytree(R/name,O/name,dirs_exist_ok=True)
for pattern in ['*.kicad_sch','*.kicad_sym']:
    for f in R.glob(pattern):shutil.copy2(f,O/f.name)
for name in ['tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:shutil.copy2(R/name,O/name)
plan=json.loads((R/'docs/design/pcb_placement.json').read_text())
rows={q['reference']:q for q in plan['placements']+plan['non_electrical_envelopes']}
b=p.LoadBoard(str(R/'tinkerbadge.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
def sig(board):
    return {f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints()}
before=sig(b);moves=[]
for q in proposal['placements']:
    f=fs[q['reference']];r=rows[q['reference']]
    assert f.GetLayer()==p.F_Cu and q['side']=='F.Cu'
    assert abs(p.ToMM(f.GetPosition().x)-q['original_x'])<0.00001
    assert abs(p.ToMM(f.GetPosition().y)-q['original_y'])<0.00001
    f.SetOrientationDegrees(q['rotation']);f.SetPosition(p.VECTOR2I(p.FromMM(q['x']),p.FromMM(q['y'])))
    moves.append({'reference':q['reference'],'before':[r['x'],r['y'],r['rotation']],'after':[q['x'],q['y'],q['rotation']]})
    for k in ['x','y','rotation','side']:r[k]=q[k]
plan['status']='lower_IR_and_rear_NFC_plan_pending_human_placement_review'
plan['notes']=[n for n in plan['notes'] if not n.startswith(('The IR receiver and emitter move left','Optical courtyards retain at least'))]
plan['notes'] += [
    'The complete nine-part IR circuit is below the display glass and above/between D405 and D406. U504 is at (137.75,168.5),180°, and D501 at (150,168.5),0°. Ambient sensing and all other placements stay unchanged.',
    'Receiver and emitter courtyards are respectively 0.805 and 1.855 mm below the glass. Their faces remain forward-looking; field of view, optical isolation and tolerances still require assembled qualification.',
    'Receiver filter/bypass and transmitter gate/current-resistor loops remain local. The longer MCU signal routes need continuous return paths and separation from switching nodes; no routing or trial escape has been done.'
]
plan['ir_placement_plan']={'location':'below display, above/between D405 and D406','receiver_mm':[137.75,168.5,180],'emitter_mm':[150,168.5,0],'moved_references':[q['reference'] for q in proposal['placements']],'ambient_sensor_unchanged':True,'glass_bottom_y_mm':164.9,'receiver_courtyard_gap_mm':0.805,'emitter_courtyard_gap_mm':1.855,'routing_status':'unrouted'}
assert sig(b)==before and len(list(b.GetTracks()))==0 and b.GroupsSanityCheck(False)==''
assert sha(proposal_path)==proposal_hash
b.BuildConnectivity();out=O/'tinkerbadge.kicad_pcb';p.SaveBoard(str(out),b)
check=p.LoadBoard(str(out));assert sig(check)==before and check.GroupsSanityCheck(False)==''
(O/'pcb_placement.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
report={'source_board_sha256':BASE,'board_sha256':sha(out),'proposal_sha256':proposal_hash,'tool':'KiCad '+p.GetBuildVersion(),'moves':moves,'move_count':len(moves),'native_group_count':len(list(check.Groups())),'pad_net_mapping_unchanged':True,'tracks':0,'NFC_geometry_unchanged':True,'status':plan['status']}
(O/'change-report.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(proposal_path,O/'reviewed-proposal.json')
print(json.dumps({k:v for k,v in report.items() if k!='moves'},indent=2))
