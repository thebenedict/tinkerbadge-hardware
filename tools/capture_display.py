#!/usr/bin/env python3
"""Reviewed display capture plan. All native KiCad writes use Konnect MCP."""
import json,pathlib,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from konnect_call import Client,unbox
root=pathlib.Path(__file__).resolve().parents[1]; sch=str(root/'display.kicad_sch'); cli=Client()
def call(name,**args):
 r=cli.call(name,args); (root/'.build'/f'mcp-display-{time.time_ns()}-{name}.json').write_text(json.dumps(r,indent=2)); u=unbox(r)
 if r.get('isError'): raise RuntimeError(json.dumps(u))
 print(name,flush=True); return u['result'][0]
def place(ref,lib,x,y,value,fp='',rotation=0): return dict(reference=ref,lib_id=lib,x=x,y=y,value=value,footprint=fp,rotation=rotation)
try:
 call('set_schematic_page',schematic=sch,size='A3')
 comps=[place('J301','Tinkerbadge:ED037TC1_FPC',177.8,85.09,'ED037TC1_FPC'),place('U301','Tinkerbadge:SN74LVC541A',76.2,76.2,'SN74LVC541APWR','Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'),place('Q301','Transistor_FET:Si1308EDL',101.6,177.8,'Si1308EDL-T1-GE3','Package_TO_SOT_SMD:SOT-323_SC-70'),place('L301','Device:L',76.2,152.4,'68uH'),place('D301','Diode:MBR0530',152.4,177.8,'MBR0530T1G','Diode_SMD:D_SOD-123',90),place('D302','Diode:MBR0530',177.8,177.8,'MBR0530T1G','Diode_SMD:D_SOD-123',270),place('D303','Diode:MBR0530',129.54,152.4,'MBR0530T1G','Diode_SMD:D_SOD-123',180)]
 # L301 horizontal with pin 1 to the left.
 comps[3]['rotation']=90
 for ref,x,y,val,rot,fp in [('R301',104.14,200.66,'0.47 / 0.25W',0,'Resistor_SMD:R_0805_2012Metric'),('R302',83.82,193.04,'10k',0,'Resistor_SMD:R_0603_1608Metric')]+[(f'R{303+i}',30.48+25.4*i,238.76,'100k',180 if i==2 else 0,'Resistor_SMD:R_0603_1608Metric') for i in range(6)]: comps.append(place(ref,'Device:R',x,y,val,fp,rot))
 caps=[('C301',50.8,170.18,'4.7u / 50V',0),('C302',129.54,165.1,'4.7u / 50V',90),('C303',208.28,55.88,'100n / 10V',0),('C304',231.14,142.24,'1u / 10V',0),('C305',256.54,142.24,'1u / 25V',0),('C306',281.94,142.24,'1u / 50V',0),('C307',307.34,142.24,'1u / 50V',0),('C308',231.14,180.34,'1u / 50V',0),('C309',256.54,180.34,'1u / 50V',0),('C310',281.94,180.34,'1u / 50V',0),('C311',307.34,180.34,'1u / 25V',0),('C312',106.68,50.8,'100n / 10V',0)]
 for ref,x,y,val,rot in caps:
  fp='Capacitor_SMD:C_1206_3216Metric' if ref in ('C301','C302') else 'Capacitor_SMD:C_0805_2012Metric' if ref not in ('C303','C312') else 'Capacitor_SMD:C_0603_1608Metric'
  comps.append(place(ref,'Device:C',x,y,val,fp,rot))
 result=call('batch_place_components',schematic=sch,components=comps)
 print(json.dumps(result)[:500])
 pins=call('batch_get_schematic_pin_locations',schematic=sch,references=[c['reference'] for c in comps]); (root/'.build/display_pin_locations.json').write_text(json.dumps(pins,indent=2)); print(json.dumps(pins)[:1800])
finally:cli.close()
