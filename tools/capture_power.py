#!/usr/bin/env python3
"""Power-sheet MCP orchestration. Native KiCad writes are performed only by Konnect."""
import json,sys,time
from pathlib import Path
from konnect_call import Client,unbox
R=Path(__file__).resolve().parents[1]
SCH=str(R/'power.kicad_sch')
contract=json.loads((R/'docs/design/power_contract.json').read_text())
lib={'U101':'Tinkerbadge_Power:TPS2121RUXR','U102':'Battery_Management:BQ24074RGT','U103':'Tinkerbadge_Power:TPS63802DLAR','U104':'Tinkerbadge_Power:TPS22918DBVR','U105':'Power_Protection:TPD4E05U06DQA','U106':'Regulator_Linear:TLV75733PDRV','U107':'Tinkerbadge_Power:TMUX1511PWR','J101':'Connector:USB_C_Receptacle_USB2.0_16P'}
positions={
'J101':(30.48,55.88),'U105':(100.33,57.15),'R101':(66.04,27.94),'R102':(88.9,27.94),'C101':(60.96,91.44),'D101':(38.1,91.44,90),'J103':(20.32,115.57),'D102':(43.18,115.57,90),'C102':(66.04,115.57),
'U101':(195.58,55.88),'C103':(260.35,43.18),'R109':(227.33,71.12),'C104':(252.73,78.74),'R103':(148.59,93.98),'R104':(148.59,109.22),'R105':(173.99,93.98),'R106':(173.99,109.22),'R107':(199.39,93.98),'R108':(199.39,109.22),'R110':(234.95,101.6),'Q103':(234.95,124.46),'R111':(260.35,116.84),
'U102':(330.2,66.04),'C105':(383.54,43.18),'C106':(383.54,83.82),'R120':(300.99,60.96,90),'J102':(398.78,64.77),'J104':(398.78,110.49),'R115':(353.06,111.76),'R116':(375.92,111.76),'R112':(292.1,91.44),'R113':(314.96,91.44),'R114':(292.1,40.64),
'U103':(63.5,185.42),'L101':(63.5,161.29,90),'C107':(25.4,186.69),'C108':(95.25,186.69),'C109':(120.65,186.69),'R117':(91.44,209.55),'R118':(91.44,224.79),'U106':(45.72,248.92),'C110':(20.32,250.19),'C111':(78.74,250.19),
'U107':(210.82,204.47),'R127':(158.75,170.18),'R128':(158.75,185.42),'C116':(180.34,185.42),'R130':(242.57,196.85,90),'R129':(260.35,214.63),'C115':(210.82,170.18),
'U104':(337.82,176.53),'C112':(294.64,175.26),'C113':(312.42,201.93),'C114':(386.08,175.26),'R119':(363.22,196.85),
'Q101':(165.1,254.0),'R121':(143.51,254,90),'R122':(146.05,269.24),'R123':(167.64,233.68),'Q102':(246.38,254),'R124':(224.79,254,90),'R125':(227.33,269.24),'R126':(248.92,233.68)}
def call(c,name,args):
 r=c.call(name,args);u=unbox(r);p=R/'.build'/f'mcp-power-{time.time_ns()}-{name}.json';p.write_text(json.dumps(r,indent=2));print(json.dumps({'tool':name,'log':str(p),**u}),flush=True)
 if r.get('isError'):raise RuntimeError('MCP reported failure; inspect state before retry')
 for x in u['result']:
  if isinstance(x,dict) and ((isinstance(x.get('errors'),list) and x['errors']) or x.get('failures') or x.get('outcome',{}).get('status') in ['partial','failed']):raise RuntimeError('MCP reported incomplete outcome; inspect before retry')
 return u['result'][0] if u['result'] else None
if __name__=='__main__':
 c=Client()
 try:
  if sys.argv[1]=='place':
   existing=call(c,'list_schematic_components',{'schematic':SCH})
   if existing.get('components'):raise RuntimeError('Sheet is not empty; do not repeat placement')
   call(c,'set_schematic_page',{'schematic':SCH,'size':'A3'})
   parts=[]
   for item in contract['components']+contract['two_terminal_support']:
    ref=item['ref'];xy=positions[ref];lid=lib.get(ref)
    if not lid:lid='Transistor_FET:AO3400A' if ref[0]=='Q' else 'Device:D_Zener' if ref[0]=='D' else 'Connector_Generic:Conn_01x02' if ref[0]=='J' else 'Device:'+item['kind']
    value=item.get('mpn') or item.get('value') or {'J102':'2-wire protected LiPo','J103':'Dock 5V contacts','J104':'NTC option - DNP'}[ref]
    parts.append({'reference':ref,'lib_id':lid,'value':value,'x':xy[0],'y':xy[1],'rotation':xy[2] if len(xy)>2 else 0,'footprint':''})
   call(c,'batch_place_components',{'schematic':SCH,'components':parts})
   pins=call(c,'batch_get_schematic_pin_locations',{'schematic':SCH,'references':[x['reference'] for x in parts]})
   (R/'.build/power_pin_locations.json').write_text(json.dumps(pins,indent=2))
  else:raise RuntimeError('Unknown stage')
 finally:c.close()
