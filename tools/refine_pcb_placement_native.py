#!/usr/bin/env python3
"""Apply reviewed placement coordinates and assembly annotation through KiCad API."""
import pcbnew as p,pathlib,json,hashlib,os
from check_schematic_contracts import sexp,children,val
root=pathlib.Path(__file__).resolve().parents[1];path=root/'tinkerbadge.kicad_pcb'
assert not (root/'~tinkerbadge.kicad_pcb.lck').exists()
hash0=hashlib.sha256(path.read_bytes()).hexdigest();b=p.LoadBoard(str(path));fs={f.GetReference():f for f in b.GetFootprints()};plan=json.loads((root/'docs/design/pcb_placement.json').read_text())
tree=sexp((root/'exports/pcb-review/tinkerbadge-placement.net').read_text());comps={val(c,'ref'):c for c in children(children(tree,'components')[0],'comp')}
for ref,c in comps.items():
 if ref in fs:
  props={val(q,'name'):val(q,'value') for q in children(c,'property')};fs[ref].SetSheetname(props.get('Sheetname',''));fs[ref].SetSheetfile(props.get('Sheetfile',''))
rows=plan['placements']+plan['non_electrical_envelopes']
rows += [{'reference':'H'+str(i),'x':x,'y':y,'rotation':0,'side':'F.Cu'} for i,(x,y,d) in enumerate(plan['mounting_holes_mm']+plan['lanyard_holes_mm'],1)]
for row in rows:
 f=fs[row['reference']];layer=p.B_Cu if row['side']=='B.Cu' else p.F_Cu
 if f.GetLayer()!=layer:f.SetLayerAndFlip(layer)
 f.SetOrientationDegrees(row['rotation']);f.SetPosition(p.VECTOR2I(p.FromMM(row['x']),p.FromMM(row['y'])))
 f.Reference().SetLayer(p.B_Fab if layer==p.B_Cu else p.F_Fab);f.Reference().SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));f.Reference().SetTextThickness(p.FromMM(.12))
 if row['reference'].startswith('TP'):f.SetExcludedFromBOM(False)
 if row['reference'].startswith('H'):f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
# Reference designators are assembly annotations on Fab; final silk will follow approved placement/routing.
assert hash0==hashlib.sha256(path.read_bytes()).hexdigest()
out=root/'.build/pcb-refinement-stage.kicad_pcb';p.SaveBoard(str(out),b);os.replace(out,path)
print(hashlib.sha256(path.read_bytes()).hexdigest())
