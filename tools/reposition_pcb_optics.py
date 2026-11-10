#!/usr/bin/env python3
"""Stage the requested optical relocation without routing or circuit changes."""
import pcbnew as p
from pathlib import Path
import hashlib, json, shutil
R=Path(__file__).resolve().parents[1]
O=R/'.build/optical-space-one-sided'
BASE='08b5de1ac1b194544ebf15598fd0b40e66a4e0c05123c6da75603a769d91554e'
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
assert not (R/'~tinkerbadge.kicad_pcb.lck').exists()
assert sha(R/'tinkerbadge.kicad_pcb')==BASE
proposal_path=R/'.build/reposition_optics_proposal.json'
proposal_hash=sha(proposal_path)
proposal=json.loads(proposal_path.read_text())
assert proposal['source_board_sha256']==BASE
for key in ['positive_area_courtyard_collisions','moved_pad_copper_outside_board','moved_pad_keepout_collisions']:
    assert not proposal[key], key
assert min(proposal['moved_reference_min_copper_edge_clearance_mm'].values())>=0.5
assert min(proposal['optical_courtyard_to_glass_mm'].values())>=0.5
O.mkdir(parents=True,exist_ok=True)
for name in ['Tinkerbadge.pretty','models']:
    shutil.copytree(R/name,O/name,dirs_exist_ok=True)
for pattern in ['*.kicad_sch','*.kicad_sym']:
    for f in R.glob(pattern): shutil.copy2(f,O/f.name)
for name in ['tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:
    shutil.copy2(R/name,O/name)
plan=json.loads((R/'docs/design/pcb_placement.json').read_text())
rows={q['reference']:q for q in plan['placements']+plan['non_electrical_envelopes']}
b=p.LoadBoard(str(R/'tinkerbadge.kicad_pcb'))
fs={f.GetReference():f for f in b.GetFootprints()}
def sig(board):
    return {f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints()}
before=sig(b);moves=[]
for q in proposal['placements']:
    f=fs[q['reference']];r=rows[q['reference']]
    assert f.GetLayer()==p.F_Cu and q['side']=='F.Cu'
    assert abs(p.ToMM(f.GetPosition().x)-q['original_x'])<0.00001
    assert abs(p.ToMM(f.GetPosition().y)-q['original_y'])<0.00001
    f.SetOrientationDegrees(q['rotation'])
    f.SetPosition(p.VECTOR2I(p.FromMM(q['x']),p.FromMM(q['y'])))
    moves.append({'reference':q['reference'],'before':[r['x'],r['y'],r['rotation']],'after':[q['x'],q['y'],q['rotation']]})
    for k in ['x','y','rotation','side']: r[k]=q[k]
assert b.GroupsSanityCheck(False)==''
plan['status']='organized_80mm_optical_space_pending_human_review_and_qualification'
plan['notes']=[n for n in plan['notes'] if not n.startswith('IR and ambient sensing move')]
plan['notes'] += [
    'The ambient sensor and its two bypass capacitors occupy the exposed shoulder immediately right of the MCU. The sensor center is (145,108.25), outside the glass.',
    'The IR receiver and emitter move left to (166,106.5) and (176,107.5), below the role row. Their low-profile support circuit occupies the free area below the optical apertures, under the raised glass.',
    'Optical courtyards retain at least 0.555 mm planar separation from the glass. Actual field of view, enclosure apertures, LED bleed, IR self-interference and assembly tolerances still require qualification.',
    'The user selected a rear-copper NFC PCB coil with the front area kept clear. Plan the eventual coil on B.Cu and retain front/inner-layer metal clearance, battery/display separation and nearby front-side tag/tuning parts. No antenna traces or tuned geometry exist yet; current all-layer reservations remain until antenna-specific rules are reviewed.'
]
plan['nfc_antenna_plan']={'decision_date_utc': '2026-11-10', 'architecture': 'integral PCB coil', 'planned_copper_layer': 'B.Cu', 'tag_and_tuning_component_side': 'F.Cu', 'projected_front_area_reserved': True, 'inner_layers_clear_of_unrelated_copper': True, 'current_reserve_mm': [182, 166, 200, 179], 'geometry_status': 'not routed or tuned', 'native_keepout_status': 'Existing all-four-layer reservation retained. Replace with antenna-network-specific rules at the approved implementation step, not a blanket removal.', 'assembly': 'Coil is fabricated copper; no additional rear SMT pass.', 'qualification': ['Exact coil geometry and feed/crossover', 'NTAG tuning and tolerances', 'Display, battery, enclosure and hardware loading', 'Read/write performance from intended tap face on target phones']}
assert sig(b)==before and len(list(b.GetTracks()))==0
assert sha(proposal_path)==proposal_hash
b.BuildConnectivity();out=O/'tinkerbadge.kicad_pcb';p.SaveBoard(str(out),b)
check=p.LoadBoard(str(out));assert sig(check)==before
assert check.GroupsSanityCheck(False)==''
(O/'pcb_placement.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
report={'source_board_sha256':BASE,'board_sha256':sha(out),'proposal_sha256':proposal_hash,'tool':'KiCad '+p.GetBuildVersion(),'moves':moves,'move_count':len(moves),'native_group_count':len(list(check.Groups())),'pad_net_mapping_unchanged':True,'tracks':0,'NFC_geometry_unchanged':True,'status':plan['status']}
(O/'change-report.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2(proposal_path,O/'reviewed-proposal.json')
print(json.dumps({k:v for k,v in report.items() if k!='moves'},indent=2))
