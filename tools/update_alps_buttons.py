#!/usr/bin/env python3
"""Bounded, one-time source-reviewed button replacement. Native writes only via Konnect MCP."""
import json,sys,hashlib,shutil
from pathlib import Path
from konnect_call import Client,unbox
r=Path(__file__).resolve().parents[1];o=r/'.build/peripheral_cad';s=str(r/'lighting.kicad_sch')
assert hashlib.sha256((r/'docs/design/peripherals_contract.json').read_bytes()).hexdigest()=='e6c3819998aac6863f164209df1b9a84b1fa9d0e6f3a30eacf522b9cf9e4f1ec','Review hash changed; stop.'
c=Client();log=[]
def call(n,a):
 raw=c.call(n,a);v=unbox(raw);log.append(dict(tool=n,arguments=a,**v));(o/'alps_capture_results.json').write_text(json.dumps(log,indent=2)+'\n')
 assert not v['isError'],v
 for x in v['result']:
  if isinstance(x,dict):assert not x.get('errors'),x
 return v['result'][0]
# A previous partial run requires readback and a bounded new recovery plan, not blind replay.
for ref in ['SW401','SW402']:
 x=call('get_schematic_component',dict(schematic=s,reference=ref));assert x['lib_id']=='Switch:SW_Push' and x['value']=='TS-1088-AR02016',x
history=o/'before_alps_buttons';history.mkdir(exist_ok=True)
for f in ['root.net','root_erc.json','endpoint_check.json','metadata_check.json','full_root_endpoint_check.json','lighting.png','lighting.pdf']:
 p=o/f
 if p.exists():shutil.copy2(p,history/f)
other={f:hashlib.sha256((r/f).read_bytes()).hexdigest() for f in ['peripherals.kicad_sch','power.kicad_sch','mcu.kicad_sch','display.kicad_sch','tinkerbadge.kicad_sch']}
for i,ref in enumerate(['SW401','SW402']):
 x=195.58+101.6*i
 call('delete_schematic_component',dict(schematic=s,reference=ref))
 call('add_schematic_component',dict(schematic=s,lib_id='Tinkerbadge_Peripherals:SKSCLBE010',reference=ref,value='SKSCLBE010',footprint='',x=x,y=177.8,rotation=0))
 pins=call('get_schematic_pin_locations',dict(schematic=s,reference=ref))['pins'];p={q['number']:(round(q['x'],2),round(q['y'],2)) for q in pins}
 assert p=={'1':(round(x+5.08,2),177.8),'2':(round(x+5.08,2),182.88),'3':(round(x-5.08,2),177.8),'4':(round(x-5.08,2),182.88)},p
 # Original switch signal wire lands on1 and ground on3; add each duplicated terminal explicitly.
 a=p['2'];b=(round(x+10.16,2),182.88);e=(b[0],177.8)
 for q,t in [(a,b),(b,e),(p['4'],(round(x-10.16,2),182.88))]:call('add_wire',dict(schematic=s,x1=q[0],y1=q[1],x2=t[0],y2=t[1]))
 call('edit_schematic_component',dict(schematic=s,reference=ref,value='SKSCLBE010',footprint='',datasheet='https://tech.alpsalpine.com/cms.media/product_spec_sksclbe010_en_f052c78d76.pdf',fields={'MPN':'SKSCLBE010','Manufacturer':'Alps Alpine','LCSC':'C115361','JLCPCB':'C115361','Rating':'12VDC/50mA max;1VDC/10uA min;2.2+/-0.65N;four terminals;side push;guide bosses','Population':'fitted','Contract':'docs/design/peripherals_contract.json','FootprintStatus':'UNASSIGNED: exact pads/locating holes/half-mount edge/case fit require physical acceptance','ApplicationStatus':'Prototype candidate: KSC-701p5D11 continuous voltage and A2 capacitive load require qualification'},field_placements={'Reference':{'x':x,'y':207.01,'rotation':0},'Value':{'x':x,'y':209.55,'rotation':0}}))
for y,t in [(215.9,'Alps side push, 2.2 N. Common pairs: 1-2 and 3-4.'),(220.98,'Always-on bias and capacitive loading need application qualification.')]:
 call('add_schematic_text',dict(schematic=s,x=177.8,y=y,text=t,size=1.27))
for f,h in other.items():assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h,f+' changed unexpectedly'
(o/'alps_other_sheet_hashes.json').write_text(json.dumps(other,indent=2)+'\n')
for n in ['validate_component_connections','validate_wire_connections','check_schematic_overlaps','validate_sheet_pins']:call(n,dict(schematic=s))
for ref in ['SW401','SW402']:call('get_schematic_component',dict(schematic=s,reference=ref))
for base in ['lighting','peripherals']:
 call('render_schematic_png',dict(schematic=str(r/(base+'.kicad_sch')),output=str(o/(base+'.png')),width_px=4096))
 call('export_schematic_pdf',dict(schematic=str(r/(base+'.kicad_sch')),output=str(o/(base+'.pdf')),all_sheets=False))
call('export_netlist',dict(board=str(r/'tinkerbadge.kicad_sch'),output=str(o/'root.net'),format='kicad'))
call('run_erc',dict(schematic=str(r/'tinkerbadge.kicad_sch'),output=str(o/'root_erc.json'),severity='warning'))
c.close();print('Native replacement and checks completed; inspect full saved results and exported endpoints.')
