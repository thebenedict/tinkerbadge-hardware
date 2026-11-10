#!/usr/bin/env python3
"""Closed-board native KiCad API import+placement for review; never raw-edits native CAD.
Refuses open/editor-locked or populated boards. Reads the pinned exported netlist.
"""
import pathlib,json,sys,hashlib,os,shutil,time
import pcbnew as pcb
from check_schematic_contracts import sexp,children,val
ROOT=pathlib.Path(__file__).resolve().parents[1];BOARD=ROOT/'tinkerbadge.kicad_pcb';NET=ROOT/'exports/pcb-review/tinkerbadge-placement.net'
plan=json.loads((ROOT/'docs/design/pcb_placement.json').read_text());FP=pathlib.Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
def guard():
 assert not (ROOT/'~tinkerbadge.kicad_pcb.lck').exists(),'PCB editor holds the board; stop'
 return hashlib.sha256(BOARD.read_bytes()).hexdigest()
baseline=guard();b=pcb.LoadBoard(str(BOARD));assert len(list(b.GetFootprints()))==0,'Refuse rebuilding populated board'
assert b.GetCopperLayerCount()==4
nettree=sexp(NET.read_text());components={val(c,'ref'):c for c in children(children(nettree,'components')[0],'comp')};nets={};endpoint={}
for q in children(children(nettree,'nets')[0],'net'):
 name=val(q,'name');n=pcb.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
 for node in children(q,'node'):endpoint[(val(node,'ref'),val(node,'pin'))]=name
root_uuid=val(sexp((ROOT/'tinkerbadge.kicad_sch').read_text()),'uuid')
logical=0

def load(libid):
 lib,name=libid.split(':',1);libpath=ROOT/'Tinkerbadge.pretty' if lib=='Tinkerbadge' else FP/(lib+'.pretty')
 f=pcb.FootprintLoad(str(libpath),name);assert f is not None,(libpath,name);f.SetFPIDAsString(libid);return f

def place(f,row):
 b.Add(f)
 if row['side']=='B.Cu':f.SetLayerAndFlip(pcb.B_Cu)
 f.SetOrientationDegrees(row['rotation']);f.SetPosition(pcb.VECTOR2I(pcb.FromMM(row['x']),pcb.FromMM(row['y'])))
 f.Reference().SetTextSize(pcb.VECTOR2I(pcb.FromMM(.8),pcb.FromMM(.8)));f.Reference().SetTextThickness(pcb.FromMM(.12));f.Value().SetVisible(False)

for row in plan['placements']:
 ref=row['reference'];comp=components[ref];libid=val(comp,'footprint');assert libid,(ref,'unassigned')
 f=load(libid);f.SetReference(ref);f.SetValue(val(comp,'value') or '')
 path=pcb.KIID_PATH();uuids=[root_uuid]+[u for u in val(children(comp,'sheetpath')[0],'tstamps').split('/') if u]+[val(comp,'tstamps')]
 for uid in uuids:path.push_back(pcb.KIID(uid))
 f.SetPath(path);props={val(x,'name'):val(x,'value') for x in children(comp,'property')}
 f.SetSheetname(props.get('Sheetname',''));f.SetSheetfile(props.get('Sheetfile',''))
 expected={pin:net for (r,pin),net in endpoint.items() if r==ref};seen=set()
 for pad in f.Pads():
  number=pad.GetNumber()
  if not number:continue
  assert number in expected,(ref,'unexpected pad',number)
  pad.SetNet(nets[expected[number]]);seen.add(number)
 assert set(expected)==seen,(ref,'missing pads',set(expected)-seen)
 logical+=len(seen)
 if ref in ['C507','C508']:f.SetDNP(True)
 place(f,row)
for row in plan['non_electrical_envelopes']:
 f=load(row['footprint']);f.SetReference(row['reference']);f.SetValue('REVIEW ENVELOPE ONLY');place(f,row)
 f.Reference().SetLayer(pcb.Dwgs_User);f.Reference().SetVisible(False)
for i,(x,y,d) in enumerate(plan['mounting_holes_mm']+plan['lanyard_holes_mm'],1):
 lid='MountingHole:MountingHole_2.2mm_M2' if d==2.2 else 'MountingHole:MountingHole_3.2mm_M3'
 f=load(lid);f.SetReference('H'+str(i));f.SetValue('PROVISIONAL');place(f,{'x':x,'y':y,'rotation':0,'side':'F.Cu'})
# Explicit all-copper no-metal region until the NFC coil design is independently reviewed.
z=pcb.ZONE(b);z.SetIsRuleArea(True);z.SetZoneName('NFC RESERVED - coil design pending');layers=pcb.LSET()
for layer in [pcb.F_Cu,pcb.In1_Cu,pcb.In2_Cu,pcb.B_Cu]:layers.AddLayer(layer)
z.SetLayerSet(layers);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowFootprints(True)
poly=z.Outline();poly.NewOutline()
for x,y in [(176,181),(206,181),(206,198),(176,198)]:poly.Append(pcb.FromMM(x),pcb.FromMM(y))
b.Add(z)
# Keep functional labels in non-fabricating review layer.
for text,x,y,size in [('PLACEMENT REVIEW - UNROUTED',155,207,2.0),('170 electrical footprints / 9 unresolved interfaces',155,211,1.2),('110 x 100 mm - outline and mechanical choices provisional',155,214,1.1),('TOP: radio / role lights / IR / ambient sensor',163,97,1.1),('BATTERY ALLOWANCE - REAR',154,163.5,1.0),('NFC ANTENNA RESERVE',191,190,1.0),('DISPLAY GLASS - FRONT',155,150.5,1.0)]:
 t=pcb.PCB_TEXT(b);t.SetText(text);t.SetLayer(pcb.Dwgs_User);t.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));t.SetTextSize(pcb.VECTOR2I(pcb.FromMM(size),pcb.FromMM(size)));t.SetTextThickness(pcb.FromMM(.15));b.Add(t)
# Pin1 indication is deliberately separate from crowded package silk.
t=pcb.PCB_TEXT(b);t.SetText('1');t.SetLayer(pcb.B_SilkS);t.SetMirrored(True);t.SetPosition(pcb.VECTOR2I(pcb.FromMM(116.3),pcb.FromMM(167.5)));t.SetTextSize(pcb.VECTOR2I(pcb.FromMM(.8),pcb.FromMM(.8)));t.SetTextThickness(pcb.FromMM(.12));b.Add(t)
b.BuildConnectivity()
assert guard()==baseline,'Board changed during preparation'
backup=ROOT/'.build/pcb-before-placement.kicad_pcb';assert not backup.exists();shutil.copy2(BOARD,backup)
stage=ROOT/'.build/pcb-native-stage.kicad_pcb';pcb.SaveBoard(str(stage),b)
check=pcb.LoadBoard(str(stage));assert len(list(check.GetFootprints()))==186
assert guard()==baseline,'Board changed before atomic replacement'
os.replace(stage,BOARD)
result={'tool':'KiCad native pcbnew Python API','version':pcb.GetBuildVersion(),'source_netlist_sha256':hashlib.sha256(NET.read_bytes()).hexdigest(),'board_sha256':hashlib.sha256(BOARD.read_bytes()).hexdigest(),'electrical_footprints':170,'logical_pads':logical,'review_envelopes':10,'holes':6,'tracks':len(list(check.GetTracks())),'copper_layers':check.GetCopperLayerCount(),'status':'placement_review_not_routed','blocked_references':plan['blocked_electrical_references']}
(ROOT/'exports/pcb-review/import-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
