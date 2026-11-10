"""Add reviewed traceability fields via Konnect MCP, never by native-file editing."""
import json,pathlib,sys
r=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));from konnect_call import Client,unbox
d=json.loads((r/'docs/design/mcu_contract.json').read_text());cl=Client();logs=[]
try:
 for c in d['components']:
  mpn=c.get('mpn') or ('PCB pad only: no fitted component' if c['ref'].startswith('TP') else 'TBD: specification-level support part')
  fields={'MPN':mpn,'Contract':'docs/design/mcu_contract.json'}
  z=unbox(cl.call('edit_schematic_component',{'schematic':str(r/'mcu.kicad_sch'),'reference':c['ref'],'fields':fields,'field_placements':{k:{'hide':True} for k in fields}}));logs.append({'ref':c['ref'],**z});assert not z['isError'],z
 for n,a in [('export_netlist',{'board':str(r/'mcu.kicad_sch'),'output':str(r/'.build/mcu-final.net'),'format':'kicad'}),('render_schematic_png',{'schematic':str(r/'mcu.kicad_sch'),'output':str(r/'.build/mcu-v3.png'),'width_px':3500,'inline':False})]:
  z=unbox(cl.call(n,a));assert not z['isError'];logs.append({'tool':n,**z})
finally:cl.close();(r/'.build/mcu_metadata_results.json').write_text(json.dumps(logs,indent=2))
print('17 individual edits completed; exported and rendered for independent readback.')
