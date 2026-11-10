from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
from konnect_call import Client,unbox
r=Path(__file__).resolve().parents[1];d=json.loads((r/'docs/design/display_contract.json').read_text());cl=Client();log=[]
try:
 for c in d['components']:
  fields={'MPN':c.get('exact_mpn') or 'TBD: specification-level support part','Contract':'docs/design/display_contract.json'}
  if c.get('rating'):fields['Rating']=str(c['rating'])
  if c['ref']=='J301':fields['Footprint_Status']='Blocked: verify exact panel/FPC contact side and mating orientation'
  o=unbox(cl.call('edit_schematic_component',dict(schematic=str(r/'display.kicad_sch'),reference=c['ref'],fields=fields)));assert not o.get('isError'),o;log.append(o)
  print(c['ref'],str(o)[:150])
 for name,args in [('export_netlist',dict(board=str(r/'display.kicad_sch'),output=str(r/'.build/display-final.net'),format='kicad')),('render_schematic_png',dict(schematic=str(r/'display.kicad_sch'),output=str(r/'.build/display-v3.png'),width_px=3500,inline=False))]:
  o=unbox(cl.call(name,args));assert not o.get('isError');print(name,'done')
finally:cl.close()
(r/'.build/display_metadata_results.json').write_text(json.dumps(log,indent=2))
