#!/usr/bin/env python3
"""Historical initial 3.95 V capture stage, not the current-build generator.
Native changes always use Konnect. Current single-3.3 V amendment is recorded
in amend_power_single_3v3.py; never rerun successful mutation stages blindly.
"""
import json,sys
from pathlib import Path
from capture_power import R,SCH,call,Client,contract,positions
if contract.get('version') != 2:
 raise RuntimeError('Historical wiring stage expects contract v2; current single-3.3 V design must not be overwritten')
pd=json.loads((R/'.build/power_pin_locations.json').read_text())
loc={(c['reference'],p['number']):p for c in pd['components'] for p in c['pins']}
items=contract['components']+contract['two_terminal_support']
nets={(c['ref'],p):n for c in items for p,n in c['pins'].items()}
# Every assigned electrical pin must exist; duplicates are accepted only on the same net.
for k in nets:assert k in loc,k
xy={}
for k,n in nets.items():
 p=loc[k];q=(round(p['x'],4),round(p['y'],4))
 if q in xy:assert xy[q][1]==n,(q,k,xy[q])
 else:xy[q]=(k,n)
parent={k:k for k in nets}
def find(k):
 while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
 return k
def union(a,b):parent[find(b)]=find(a)
for k,n in nets.items():
 p=loc[k];q=(round(p['x'],4),round(p['y'],4));union(xy[q][0],k)
q=[]
def req(name,args):q.append({'name':name,'arguments':{'schematic':SCH,**args}})
def edge(a,b):
 a=(a[0],str(a[1]));b=(b[0],str(b[1]));assert nets[a]==nets[b] and nets[a]
 req('connect_pins',{'ref1':a[0],'pin1':a[1],'ref2':b[0],'pin2':b[1]});union(a,b)
for a,b in [(('R103',2),('R104',1)),(('R105',2),('R106',1)),(('R107',2),('R108',1)),(('R117',2),('R118',1)),(('R127',2),('R128',1)),(('R128',1),('C116',1)),(('U107',3),('R130',1)),(('R130',2),('R129',1)),(('R120',2),('U102',4)),(('C107',1),('U103',10)),(('U103',6),('C108',1)),(('C108',1),('C109',1)),(('U106',6),('C110',1)),(('U106',1),('C111',1)),(('U104',1),('C112',1)),(('U104',6),('C114',1)),(('U104',4),('C113',1)),(('R121',2),('Q101',1)),(('R121',2),('R122',1)),(('R123',2),('Q101',3)),(('R124',2),('Q102',1)),(('R124',2),('R125',1)),(('R126',2),('Q102',3))]:edge(a,b)
# Switching-node loop, routed above the converter without crossing its body.
for pin,ind,endx in [('9','1',44.45),('7','2',82.55)]:
 a=('U103',pin);b=('L101',ind);p=loc[a];t=loc[b]
 points=[(p['x'],p['y']),(endx,p['y']),(endx,t['y']),(t['x'],t['y'])]
 for p1,p2 in zip(points,points[1:]):req('add_wire',{'x1':p1[0],'y1':p1[1],'x2':p2[0],'y2':p2[1]})
 union(a,b)
# Group pins sharing either an explicit wire or an already stacked endpoint.
groups={}
for k in nets:groups.setdefault(find(k),[]).append(k)
cross={'USB_VBUS','DOCK_5V','VLED_3V9','+3V3_EPD','USB_DP','USB_DM','USB_PRESENT_N','DOCK_PRESENT_N','BAT_ADC','CHARGER_CHG_N','CHARGER_PGOOD_N','EPD_EN'}
for group in groups.values():
 k=group[0];n=nets[k];p=loc[k]
 if n is None:
  # TLV757 NC pins are already intrinsic no-connect pins, hidden inside its symbol.
  if k not in [('U106','2'),('U106','5')]:req('add_no_connect',{'x':p['x'],'y':p['y']})
  continue
 if n in ['GND','+3V3']:
  # Extend ground down and supply up from a small outward stub where needed.
  dx={0:2.54,180:-2.54}.get(round(p['orientation_degrees']),0)
  dy=2.54 if n=='GND' else -2.54
  xx=round(p['x']+dx,5);yy=round(p['y']+dy,5)
  if dx:req('add_wire',{'x1':p['x'],'y1':p['y'],'x2':xx,'y2':p['y']})
  req('add_wire',{'x1':xx,'y1':p['y'],'x2':xx,'y2':yy})
  req('add_power_symbol',{'power_net':n,'x':xx,'y':yy})
 else:
  req('connect_to_net',{'reference':k[0],'pin_number':k[1],'net':n,'label_type':'global_label' if n in cross else 'net_label','stub_length':2.54})
# Place IC reference/value fields in clear corners, away from top and bottom pins.
for ref in ['U101','U103','U104','U107']:
 x,y=positions[ref][:2];off=17.78 if ref!='U104' else 12.7
 req('edit_schematic_component',{'reference':ref,'field_placements':{'Reference':{'x':x+17.78,'y':y-off-2.54},'Value':{'x':x+17.78,'y':y-off}}})
# Preserve descriptive DNP/footprint gates without claiming an unavailable native DNP toggle.
req('edit_schematic_component',{'reference':'J104','fields':{'Populate':'DNP','Safety':'Optional cell-contact thermistor. Charging remains hard disabled.'}})
for ref in ['J102','J103','J104','L101']:
 req('edit_schematic_component',{'reference':ref,'fields':{'FootprintStatus':'Unassigned: exact physical part and polarity acceptance pending'}})
for x,y,title in [(15.24,16.51,'USB / dock inputs'),(139.7,16.51,'USB-priority source selection'),(281.94,16.51,'Power path: charging disabled'),(15.24,146.05,'Shared 3.95 V rail / 3.3 V logic'),(149.86,146.05,'Battery ADC / source presence'),(281.94,146.05,'Display power')]:req('add_schematic_text',{'x':x,'y':y,'text':title,'size':2,'bold':True})
req('add_schematic_text',{'x':281.94,'y':220.98,'text':'DEVELOPMENT SAFETY GATES\nR120 fitted: charging OFF. J104 thermistor DNP.\nFitting a sensor alone does not enable charging.\nJ102 terminal numbers are logical, not vendor polarity.\nFootprints / exact pack / thermal and peak loads: pending.\nUSB 100 mA and dock 500 mA modes need bench validation.','size':1.27})
req('add_schematic_text',{'x':15.24,'y':280.67,'text':'Electrical development draft. No PCB layout or manufacturing release. See docs/design/power.md.','size':1.27})
req('render_schematic_png',{'output':str(R/'.build/power_first_capture.png'),'width_px':4096})
req('export_netlist',{'board':SCH,'output':str(R/'.build/power.net'),'format':'kicad'})
# export_netlist uses board rather than schematic.
q[-1]['arguments'].pop('schematic')
(R/'.build/power_wiring_requests.json').write_text(json.dumps(q,indent=2))
if __name__=='__main__':
 c=Client()
 try:
  for a in q:call(c,a['name'],a['arguments'])
 finally:c.close()
