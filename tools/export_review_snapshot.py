#!/usr/bin/env python3
"""Export current saved native project via Konnect MCP; never creates CAD."""
from pathlib import Path
import json,sys,hashlib
from konnect_call import Client,unbox
root=Path(__file__).resolve().parents[1];out=root/'exports';out.mkdir(exist_ok=True)
inputs=sorted([*root.glob('*.kicad_sch'),*root.glob('*.kicad_sym'),root/'sym-lib-table',root/'tinkerbadge.kicad_pro',*root.glob('docs/design/*_contract.json')])
def input_hashes():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
before=input_hashes()
cl=Client();records=[]
try:
 calls=[('get_sheet_hierarchy',{'schematic':str(root/'tinkerbadge.kicad_sch')}),('export_netlist',{'board':str(root/'tinkerbadge.kicad_sch'),'output':str(out/'tinkerbadge.net'),'format':'kicad'}),('run_erc',{'schematic':str(root/'tinkerbadge.kicad_sch'),'output':str(out/'erc.json'),'severity':'warning'}),('export_schematic_pdf',{'schematic':str(root/'tinkerbadge.kicad_sch'),'output':str(out/'tinkerbadge-schematic.pdf'),'all_sheets':True,'black_and_white':False})]
 for name,args in calls:
  result=unbox(cl.call(name,args));assert not result.get('isError'),(name,result);records.append({'tool':name,'arguments':args,'result':result});print(name,json.dumps(result)[:1800],flush=True)
 for name in ['tinkerbadge','power','mcu','display','lighting','peripherals']:
  args={'schematic':str(root/(name+'.kicad_sch')),'output':str(out/(name+'.png')),'width_px':3500,'inline':False}
  result=unbox(cl.call('render_schematic_png',args));assert not result.get('isError');records.append({'tool':'render_schematic_png','arguments':args,'result_summary':'Saved PNG verified separately'});print('Rendered',name,flush=True)
finally:cl.close()
after=input_hashes()
assert before==after,'Native files or contracts changed during export; do not use this snapshot.'
(out/'native-inputs.json').write_text(json.dumps({'sha256':after,'unchanged_during_export':True},indent=2)+'\n')
(out/'export_tools.json').write_text(json.dumps(records,indent=2)+'\n')
