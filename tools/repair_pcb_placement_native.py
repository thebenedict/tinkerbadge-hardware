#!/usr/bin/env python3
"""Rebuild imported footprint forms from reviewed libraries with native KiCad API.
Keeps board geometry/nets and schematic UUID paths; refuses any running editor lock.
Used because the live import omitted models and footprint-owned rule areas.
"""
import pcbnew as p,pathlib,json,hashlib,os,shutil,time
from check_schematic_contracts import sexp,children,val
root=pathlib.Path(__file__).resolve().parents[1];path=root/'tinkerbadge.kicad_pcb';libroot=pathlib.Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
assert not (root/'~tinkerbadge.kicad_pcb.lck').exists(),'Open PCB editor; stop'
baseline=hashlib.sha256(path.read_bytes()).hexdigest();b=p.LoadBoard(str(path));plan=json.loads((root/'docs/design/pcb_placement.json').read_text());old={f.GetReference():f for f in b.GetFootprints()}
assert len(old)==186 and len(list(b.GetTracks()))==0
n=sexp((root/'exports/pcb-review/tinkerbadge-placement.net').read_text());comps={val(c,'ref'):c for c in children(children(n,'components')[0],'comp')};ep={}
for net in children(children(n,'nets')[0],'net'):
 for node in children(net,'node'):ep[(val(node,'ref'),val(node,'pin'))]=val(net,'name')
nets={net.GetNetname():net for net in b.GetNetsByNetcode().values()}
def load(lid):
 lib,name=lid.split(':',1);f=p.FootprintLoad(str(root/'Tinkerbadge.pretty' if lib=='Tinkerbadge' else libroot/(lib+'.pretty')),name);assert f is not None,lid;f.SetFPIDAsString(lid);return f
new=[]
def place(f,row):
 ref=row['reference'];f.SetReference(ref)
 if ref in old:
  f.SetPath(old[ref].GetPath());f.SetSheetname(old[ref].GetSheetname());f.SetSheetfile(old[ref].GetSheetfile())
 b.Add(f)
 if row['side']=='B.Cu':f.SetLayerAndFlip(p.B_Cu)
 f.SetOrientationDegrees(row['rotation']);f.SetPosition(p.VECTOR2I(p.FromMM(row['x']),p.FromMM(row['y'])))
 f.Reference().SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));f.Reference().SetTextThickness(p.FromMM(.12));f.Value().SetVisible(False)
 if ref.startswith(('MECH_','RES_')):f.Reference().SetVisible(False)
 new.append(f)
for row in plan['placements']:
 ref=row['reference'];f=load(val(comps[ref],'footprint'));f.SetValue(val(comps[ref],'value') or '')
 if ref.startswith('TP'):f.SetExcludedFromBOM(False)
 
 for q in children(comps[ref],'property'):
  key,value=val(q,'name'),val(q,'value')
  if key not in ['Sheetname','Sheetfile'] and not key.startswith('ki_'):
   f.SetField(key,value or '');f.GetField(key).SetVisible(False)
 f.SetField('Datasheet',val(comps[ref],'datasheet') or '');f.SetField('Description',val(comps[ref],'description') or '')
 expected={pin:net for (r,pin),net in ep.items() if r==ref};seen=set()
 for pad in f.Pads():
  number=pad.GetNumber()
  if not number:continue
  assert number in expected,(ref,'extra pad',number)
  pad.SetNet(nets[expected[number]]);seen.add(number)
 assert set(expected)==seen,(ref,'missing pad',set(expected)-seen)
 place(f,row)
for row in plan['non_electrical_envelopes']:
 f=load(row['footprint']);f.SetValue('REVIEW ONLY');place(f,row)
for i,(x,y,d) in enumerate(plan['mounting_holes_mm']+plan['lanyard_holes_mm'],1):
 f=load('MountingHole:MountingHole_2.2mm_M2' if d==2.2 else 'MountingHole:MountingHole_3.2mm_M3');f.SetValue('PROVISIONAL');f.SetAttributes(f.GetAttributes() | p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES);place(f,{'reference':'H'+str(i),'x':x,'y':y,'rotation':0,'side':'F.Cu'})
for f in old.values():b.Remove(f)
b.BuildConnectivity();assert len(list(b.GetFootprints()))==186
assert hashlib.sha256(path.read_bytes()).hexdigest()==baseline and not (root/'~tinkerbadge.kicad_pcb.lck').exists()
stage=root/'.build/pcb-repaired-stage.kicad_pcb';p.SaveBoard(str(stage),b)
check=p.LoadBoard(str(stage));assert len(list(check.GetFootprints()))==186
assert sum(len(list(f.Models())) for f in check.GetFootprints())==167
assert len(list(next(f for f in check.GetFootprints() if f.GetReference()=='U201').Zones()))==1
assert len(list(next(f for f in check.GetFootprints() if f.GetReference()=='MECH_NFC').Zones()))==1
shutil.copy2(path,root/f'.build/pcb-before-native-repair-{time.time_ns()}.kicad_pcb');os.replace(stage,path)
report={'tool':'official KiCad pcbnew native API','kicad':p.GetBuildVersion(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'footprints':186,'electrical':170,'tracks':0,'model_references':sum(len(list(f.Models())) for f in check.GetFootprints()),'footprint_rule_areas':sum(len(list(f.Zones())) for f in check.GetFootprints()),'layers':check.GetCopperLayerCount(),'source_netlist_sha256':hashlib.sha256((root/'exports/pcb-review/tinkerbadge-placement.net').read_bytes()).hexdigest()}
(root/'exports/pcb-review/native-repair-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
