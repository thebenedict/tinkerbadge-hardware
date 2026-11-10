#!/usr/bin/env python3
"""Stage the 110x80 front-SMT experiment with native KiCad geometry. Never route.
The preserved 100 mm board remains an independently reproducible fallback.
"""
import pcbnew as p, pathlib, json, hashlib, shutil, copy
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='99158950ecce21da92f8c0e9343ecf60316f321255fd496f790517ac7717f49f'
BOARD=ROOT/'tinkerbadge.kicad_pcb'
STAGE=ROOT/'.build/compact-one-sided'
HIST=ROOT/'docs/design/history/2026-11-09-100mm-two-sided-fallback'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert not (ROOT/'~tinkerbadge.kicad_pcb.lck').exists(),'Open PCB editor; stop.'
assert sha(BOARD)==BASE,'Source changed; review instead of overwriting.'
# Immutable fallback snapshot includes original local models and mechanical footprints.
if not HIST.exists():
 HIST.mkdir(parents=True)
 for name in ['tinkerbadge.kicad_pcb','tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:
  shutil.copy2(ROOT/name,HIST/name)
 for f in ROOT.glob('*.kicad_sch'):shutil.copy2(f,HIST/f.name)
 for name in ['Tinkerbadge.pretty','models']:
  src=ROOT/name
  if src.is_dir():shutil.copytree(src,HIST/name)
  elif src.exists():shutil.copy2(src,HIST/name)
 for f in ROOT.glob('*.kicad_sym'):shutil.copy2(f,HIST/f.name)
 shutil.copy2(ROOT/'docs/design/pcb_placement.json',HIST/'pcb_placement.json')
 shutil.copy2(ROOT/'exports/tinkerbadge.net',HIST/'tinkerbadge.net')
 shutil.copy2(ROOT/'docs/design/pcb_placement_review.md',HIST/'pcb_placement_review.md')
 (HIST/'README.md').write_text('# Preserved 100 mm two-sided placement\n\nNative board SHA256 '+BASE+'. This was the last checked placement before the requested one-sided, compact experiment. It is unrouted and not approved for production. Local libraries/models and schematic records are frozen with it.\n')
STAGE.mkdir(parents=True,exist_ok=True)
for name in ['Tinkerbadge.pretty','models']:
 shutil.copytree(ROOT/name,STAGE/name,dirs_exist_ok=True)
for f in ROOT.glob('*.kicad_sch'):shutil.copy2(f,STAGE/f.name)
for f in ROOT.glob('*.kicad_sym'):shutil.copy2(f,STAGE/f.name)
for name in ['tinkerbadge.kicad_pro','fp-lib-table','sym-lib-table']:
 if (ROOT/name).exists():shutil.copy2(ROOT/name,STAGE/name)
plan=json.loads((ROOT/'docs/design/pcb_placement.json').read_text())
power=json.loads((ROOT/'.build/one_sided_power_plan.json').read_text())
assert power['source_board_sha256']==BASE
plan['status']='experimental_80mm_one_sided_placement_pending_human_review_and_RF_qualification'
plan['board_mm']=[110,80]
plan['glass_underside_mm']=4.5
plan['outline_note']='True top-open notch x105..155 to y106.75; internal radius0.5. RF free-space/assembled performance unqualified.'
rows={r['reference']:r for r in plan['placements']+plan['non_electrical_envelopes']}
for r in rows.values():
 if not r['reference'].startswith('TP') and r['reference'] not in ['MECH_BATTERY','RES_J502','RES_J103']:
  r['side']='F.Cu'
for q in power['placements']:
 r=rows[q['reference']]
 for k in ['x','y','rotation','side','group']:r[k]=q[k]
# Fixed optics/mechanics and their support circuits.
own={
'U201':(130,113.25,0),'SW401':(102.1,145,270),'SW402':(102.1,155,270),
'C201':(115.5,111,90),'C202':(118.5,108.8,0),'C203':(115.5,115.5,0),
'R201':(116.5,119,0),'R202':(138,129,0),'R205':(111.5,119,0),'R206':(111.5,122.5,0),
'R203':(126,129,0),'R204':(129.5,129,0),'R207':(138,132.5,0),
'D401':(144,108.5,0),'D402':(172.5,108.5,0),'D403':(201,108.5,0),
'C401':(146.5,111.5,90),'C402':(175,111.5,90),'C403':(201,112,90),
'C409':(145.5,120,0),'D409':(104,122,90),'R401':(142,117,0),'R402':(143,114,0),
'R403':(105,125,0),'R404':(105,128,0),'R405':(114,145,0),'R406':(114,155,0),
'R411':(106,149,0),'C411':(109.5,149,0),'R412':(113,149,0),
'R413':(106,159,0),'C412':(109.5,159,0),'R414':(113,159,0),
'U501':(205,103,0),'C501':(205,106.5,0),'U504':(185,105.5,0),'D501':(195,105.5,0),
'R507':(180.5,110.5,0),'C509':(184,110.5,0),'C510':(187.5,110.5,0),
'Q501':(195,110.5,0),'R504':(195,114.5,0),'R505':(191,110.5,0),'R506':(191,114,0),
'U502':(162,121,0),'C502':(159,121,0),'C503':(159,124,0),
'R501':(155,128,0),'R502':(158.5,128,0),
'U503':(191,163.5,0),'R503':(198,160.8,0),'C504':(187,160,0),'C505':(190.5,160,0),
'C506':(194,161.5,0),'C507':(188,164,0),'C508':(195,164,0),
'U505':(195,158,0),'J501':(206.5,159,90),
'C511':(192,151,0),'C512':(192,148,0),'C513':(200.5,158,0),
'R508':(187,154,0),'R509':(190.5,154,0),'R510':(187,157.5,0),'R511':(190.5,157.5,0),
'R512':(202.3,162.6,90),'R513':(199.2,162.5,0),
'U506':(146,124,0),'C514':(151.5,122,0),'C515':(151.5,125.5,0),
'R514':(143,130,0),'R515':(146,130,0),'R516':(149,130,0),'R517':(152,130,0),
'MECH_PANEL':(156,137.45,0),'MECH_BATTERY':(154,147.5,0),'MECH_NFC':(191,172.5,0),
'RES_J301':(202,145,0),'RES_J502':(151.5,114,0),'RES_J102':(130,138,0),'RES_J103':(124,175,0),
}
for i,x in enumerate([108,131.5,155,178.5,202],404):
 own['D'+str(i)]=(x,174,0)
 own['C'+str(i)]=(x+2.5,174,90)
own['C407']=(178.5,177,0)
# Independently reviewed local TPS2121 bypass allocation, same existing parts/nets.
own.update({'C101':(187,124.4,0),'C102':(180.8,125.2,270),'C105':(177.4,127.5,180),'R115':(177.4,130.2,0),'R112':(180.5,129.6,0),'R111':(175.5,133.5,0)})
for i,x in enumerate([174,177,180,183,186,189],201):own['TP'+str(i)]=(x,116,0)
for ref,(x,y,rot) in own.items():
 rows[ref].update(x=x,y=y,rotation=rot)
plan['mounting_holes_mm']=[[104,117.5,2.2],[206,117.5,2.2],[104,166,2.2],[206,166,2.2]]
plan['lanyard_holes_mm']=[[104,112,3.2],[206,112,3.2]]
plan['notes']=[
'Experimental 110x80 placement. Human approval required before routing; no routing performed.',
'All164 non-testpoint electrical footprints are front-side. Six unpopulated copper test pads remain rear. SAO is a future rear through-hole secondary assembly.',
'Panel underside4.5mm proposal above front PCB, thickness0.92mm envelope. Exact supports, solder/warp/tolerance stack and flex remain unqualified.',
'The full module native keepout remains all-layer; true board notch removes FR4. Glass is only3.5mm behind antenna, below the recommended15mm housing clearance. No RF-compliance claim.',
'NFC18x13 reserve replaces30x17. No coil copper exists; inductance/coupling/read range/tuning remain open.',
'Bottom LED pitch23.5mm from x108 to202. Leftmost X stays108; Y moves from190 to174 for the compact board.',
'Role LED X positions unchanged; Y moves114 to108.5 for compact mechanical margin. This supersedes the prior fixed-left-LED location request for the approved compact trial only.',
'Textile-only cord reservationsØ5.2, drillØ3.2; no metal clip. Structural holesØ2.2 with maximumØ4.5 nonconductive head/boss assumed.',
'Existing USB hole-to-pad DRC exceptions remain unresolved. Nine electrical footprints remain unassigned. Charging disabled.',
]
b=p.LoadBoard(str(BOARD));fs={f.GetReference():f for f in b.GetFootprints()}
def V(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def signature(board):
 return {f.GetReference():sorted((a.GetNumber(),a.GetNetname()) for a in f.Pads() if a.GetNumber()) for f in board.GetFootprints() if not f.GetReference().startswith(('MECH_','RES_','H'))}
before=signature(b)
lib=STAGE/'Tinkerbadge.pretty'
# The four native library assets were prepared in a separate process.
for ref,name in [('MECH_PANEL','Review_Panel_Raised_4p5'),('MECH_NFC','Review_NFC_18x13'),('RES_J502','Review_SAO_Front_Tail_Reserve')]:
 assert (lib/(name+'.kicad_mod')).exists()
 rows[ref]['footprint']='Tinkerbadge:'+name
cordlid='Tinkerbadge:Review_Cord_Hole_3p2'
assert (lib/'Review_Cord_Hole_3p2.kicad_mod').exists()
removed=[]
def replace(ref,lid):
 old=fs[ref];b.Remove(old);removed.append(old)
 f=p.FootprintLoad(str(lib),lid.split(':')[1]);f.SetReference(ref);f.SetValue('REVIEW ENVELOPE ONLY');f.SetFPIDAsString(lid);b.Add(f);fs[ref]=f
for ref in ['MECH_PANEL','MECH_NFC','RES_J502']:replace(ref,rows[ref]['footprint'])
for ref in ['H5','H6']:replace(ref,cordlid)
for i,(x,y,d) in enumerate(plan['mounting_holes_mm']+plan['lanyard_holes_mm'],1):
 rows['H'+str(i)]={'reference':'H'+str(i),'x':x,'y':y,'rotation':0,'side':'F.Cu'}
for ref,row in rows.items():
 f=fs[ref];layer=p.B_Cu if row['side']=='B.Cu' else p.F_Cu
 if f.GetLayer()!=layer:f.SetLayerAndFlip(layer)
 f.SetOrientationDegrees(row['rotation']);f.SetPosition(V(row['x'],row['y']))
 if ref.startswith(('MECH_','RES_')):
  f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
  f.Reference().SetLayer(p.Dwgs_User);f.Reference().SetVisible(False)
 else:
  f.Reference().SetLayer(p.B_Fab if layer==p.B_Cu else p.F_Fab)
  f.Reference().SetTextSize(V(.8,.8));f.Reference().SetTextThickness(p.FromMM(.12))
# Rule areas belong to the module and NFC footprints; keep those with the footprints.
assert len(list(b.Zones()))==0
# A single closed outer outline including true top-open notch. No overlapping rectangle.
for d in list(b.GetDrawings()):
 if d.GetLayer()==p.Edge_Cuts or isinstance(d,p.PCB_TEXT):
  b.Remove(d);removed.append(d)
def seg(a,c):
 d=p.PCB_SHAPE(b);d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(V(*a));d.SetEnd(V(*c));d.SetLayer(p.Edge_Cuts);d.SetWidth(p.FromMM(.05));b.Add(d)
def arc(a,m,c):
 d=p.PCB_SHAPE(b);d.SetShape(p.SHAPE_T_ARC);d.SetArcGeometry(V(*a),V(*m),V(*c));d.SetLayer(p.Edge_Cuts);d.SetWidth(p.FromMM(.05));b.Add(d)
seg((104,100),(105,100));seg((105,100),(105,106.25))
arc((105,106.25),(105.1464466,106.6035534),(105.5,106.75))
seg((105.5,106.75),(154.5,106.75))
arc((154.5,106.75),(154.8535534,106.6035534),(155,106.25))
seg((155,106.25),(155,100));seg((155,100),(206,100))
arc((206,100),(208.8284271,101.1715729),(210,104));seg((210,104),(210,176))
arc((210,176),(208.8284271,178.8284271),(206,180));seg((206,180),(104,180))
arc((104,180),(101.1715729,178.8284271),(100,176));seg((100,176),(100,104))
arc((100,104),(101.1715729,101.1715729),(104,100))
for text,x,y,size in [
 ('EXPERIMENTAL110x80 - UNROUTED - HUMAN REVIEW REQUIRED',155,187,1.5),
 ('Front SMT / display underside4.5mm proposed / RF and flex unqualified',155,191,1),
 ('NOTCH removes FR4; display does NOT meet15mm antenna clearance',155,194,1),
 ('DISPLAY GLASS ABOVE FRONT PARTS',156,137.45,1),
 ('BATTERY ALLOWANCE - REAR',154,147.5,1),('NFC18x13 RESERVE',191,173,1)]:
 t=p.PCB_TEXT(b);t.SetText(text);t.SetLayer(p.Dwgs_User);t.SetPosition(V(x,y));t.SetTextSize(V(size,size));t.SetTextThickness(p.FromMM(.15));b.Add(t)
b.BuildConnectivity()
assert signature(b)==before,'Electrical endpoint mapping changed'
assert len(list(b.GetTracks()))==0
assert b.GetCopperLayerCount()==4
assert sha(BOARD)==BASE,'Source changed during staging'
out=STAGE/'tinkerbadge.kicad_pcb';p.SaveBoard(str(out),b)
check=p.LoadBoard(str(out));assert signature(check)==before
(STAGE/'pcb_placement.json').write_text(json.dumps(plan,indent=2)+'\n')
report={
 'status':plan['status'],'source_sha256':BASE,'board_sha256':sha(out),'tool':'KiCad '+p.GetBuildVersion(),
 'board_mm':[110,80],'footprints':len(list(check.GetFootprints())),'electrical':len(before),
 'front_electrical':sum(f.GetLayer()==p.F_Cu for f in check.GetFootprints() if f.GetReference() in before),
 'back_electrical':sum(f.GetLayer()==p.B_Cu for f in check.GetFootprints() if f.GetReference() in before),
 'endpoint_count':sum(len(v) for v in before.values()),'nets_unchanged':True,'tracks':0,
 'source_netlist_sha256':sha(ROOT/'exports/tinkerbadge.net'),
 'new_local_footprints':[rows[r]['footprint'] for r in ['MECH_PANEL','MECH_NFC','RES_J502']]+[cordlid],
 'pending':'Native DRC, independent final placement review, height/flex/RF verification, human approval. No routing.'
}
(STAGE/'candidate-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

