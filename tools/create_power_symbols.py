#!/usr/bin/env python3
"""Prepare MCP requests for source-verified power symbols. No native files edited."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lib=str(root/'power_symbols.kicad_sym')
requests=[]
def pin(n,name,typ,x,y,a=0):return {'number':str(n),'name':name,'type':typ,'x':x,'y':y,'angle':a,'length':3.81}
def part(name,w,h,pins,url):
 requests.append({'name':'create_symbol','arguments':{'library_path':lib,'name':name,'reference_prefix':'U','value':name,'datasheet':url,'graphics':[{'type':'rect','start':{'x':-w,'y':h},'end':{'x':w,'y':-h},'stroke_width_mm':0.254,'fill':'background'}],'pins':pins}})
part('TPS2121RUXR',10.16,15.24,[pin(7,'IN1','power_in',-13.97,10.16),pin(2,'IN2','power_in',-13.97,7.62),pin(6,'PR1','input',-13.97,2.54),pin(3,'CP2','input',-13.97,0),pin(5,'OV1','input',-13.97,-5.08),pin(4,'OV2','input',-13.97,-7.62),pin(1,'OUT','power_out',13.97,10.16,180),pin(8,'OUT','passive',13.97,7.62,180),pin(9,'ST','open_collector',13.97,2.54,180),pin(10,'ILM','passive',13.97,-2.54,180),pin(11,'SS','passive',13.97,-7.62,180),pin(12,'GND','power_in',0,-19.05,90)],'https://www.ti.com/lit/ds/symlink/tps2121.pdf')
part('TPS63802DLAR',10.16,12.7,[pin(9,'L1','passive',-13.97,7.62),pin(7,'L2','passive',13.97,7.62,180),pin(10,'VIN','power_in',-13.97,2.54),pin(6,'VOUT','power_out',13.97,2.54,180),pin(1,'EN','input',-13.97,-2.54),pin(4,'FB','input',13.97,-2.54,180),pin(2,'MODE','input',-13.97,-7.62),pin(5,'PG','open_collector',13.97,-7.62,180),pin(3,'AGND','power_in',-2.54,-16.51,90),pin(8,'GND','power_in',2.54,-16.51,90)],'https://www.ti.com/lit/ds/symlink/tps63802.pdf')
part('TPS22918DBVR',7.62,7.62,[pin(1,'VIN','power_in',-11.43,5.08),pin(3,'ON','input',-11.43,0),pin(4,'CT','passive',-11.43,-5.08),pin(6,'VOUT','power_out',11.43,5.08,180),pin(5,'QOD','passive',11.43,0,180),pin(2,'GND','power_in',0,-11.43,90)],'https://www.ti.com/lit/ds/symlink/tps22918.pdf')
part('TMUX1511PWR',10.16,15.24,[pin(1,'SEL1','input',-13.97,10.16),pin(2,'S1','passive',-13.97,7.62),pin(3,'D1','passive',13.97,7.62,180),pin(4,'SEL2','input',-13.97,2.54),pin(5,'S2','passive',-13.97,0),pin(6,'D2','passive',13.97,0,180),pin(10,'SEL3','input',-13.97,-5.08),pin(9,'S3','passive',-13.97,-7.62),pin(8,'D3','passive',13.97,-7.62,180),pin(13,'SEL4','input',-13.97,-10.16),pin(12,'S4','passive',-13.97,-12.7),pin(11,'D4','passive',13.97,-12.7,180),pin(14,'VDD','power_in',0,19.05,270),pin(7,'GND','power_in',0,-19.05,90)],'https://www.ti.com/lit/ds/symlink/tmux1511.pdf')
(root/'.build/create_power_symbols.json').write_text(json.dumps(requests,indent=2))
print('Prepared',len(requests),'MCP symbol requests; footprints remain unassigned pending physical acceptance.')
