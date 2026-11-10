#!/usr/bin/env python3
"""Bounded native placement change: LED rows and their local decouplers only."""
import pathlib,json,hashlib,os
import pcbnew as p
root=pathlib.Path(__file__).resolve().parents[1];path=root/'tinkerbadge.kicad_pcb';planpath=root/'docs/design/pcb_placement.json'
assert not (root/'~tinkerbadge.kicad_pcb.lck').exists()
base='322dc5d129db733813ff2d9dc0912e813fc9aa27043376b74c5deea2b9d668fa';assert hashlib.sha256(path.read_bytes()).hexdigest()==base,'Unexpected source revision'
b=p.LoadBoard(str(path));fs={f.GetReference():f for f in b.GetFootprints()}
def positions():return {r:[f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),int(f.GetLayer())] for r,f in fs.items()}
def padnets():return sorted((f.GetReference(),q.GetNumber(),q.GetNetname()) for f in fs.values() for q in f.Pads())
before=positions();nets=padnets();changes={'D402':(172.5,114),'D403':(201,114),'C402':(175.5,114),'C403':(201,117.5)}
for n,x in zip(range(404,409),[108,124,140,156,172]):
 changes['D'+str(n)]=(x,190);changes['C'+str(n)]=(x+2.5,190)
for ref,(x,y) in changes.items():fs[ref].SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
after=positions();assert before['D401']==after['D401'];assert before['C401']==after['C401'];assert padnets()==nets
assert all(before[r]==after[r] for r in fs if r not in changes)
assert not list(b.GetTracks())
plan=json.loads(planpath.read_text())
for row in plan['placements']:
 if row['reference'] in changes:row['x'],row['y']=changes[row['reference']]
plan['notes'].append('LED spacing revision: D401 stays exactly at F(144,114). Role centers144/172.5/201 have28.5mm pitch. Affinity centers108/124/140/156/172 at y190 have16mm pitch within the NFC-clear span; lower-right NFC reservation is unchanged.')
stage=root/'.build/pcb-led-spacing-stage.kicad_pcb';p.SaveBoard(str(stage),b)
check=p.LoadBoard(str(stage));assert len(list(check.GetFootprints()))==186
assert hashlib.sha256(path.read_bytes()).hexdigest()==base
os.replace(stage,path);planpath.write_text(json.dumps(plan,indent=2)+'\n')
report={'status':'native_LED_placement_updated_pending_independent_checks','previous_board_sha256':base,'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'moved_references':sorted(changes),'positions_before_nm':{r:before[r] for r in changes},'positions_after_nm':{r:after[r] for r in changes},'leftmost_role_LED_unchanged':before['D401']==after['D401'],'all_other_footprints_unchanged':all(before[r]==after[r] for r in fs if r not in changes),'all_pad_nets_unchanged':padnets()==nets,'role_pitch_mm':28.5,'affinity_pitch_mm':16,'affinity_row_note':'Even spacing widened within NFC-clear bottom span, not full board width.','routing_tracks':0}
(root/'exports/pcb-review/led-spacing-change.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if not k.startswith('positions_')},indent=2))
