#!/usr/bin/env python3
"""Reviewed one-shot power amendment, all native writes via Konnect MCP.
Do not repeat a successful stage. Original revision remains under docs/design/history.
"""
import json,hashlib,sys
from capture_power import R,SCH,Client,call
CONTRACT='20fb7654f96922426fbc6a5b73ef70995b394aab9696421ed483bcbc73615563'
PRIOR_SHEET='137e7f1daf40aac11d6c4be061468b6c48a9999a3ebdb6682e1a062be78fc4c8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def perform():
 assert sha(R/'docs/design/power_contract.json')==CONTRACT,'Reviewed contract changed'
 assert sha(R/'power.kicad_sch')==PRIOR_SHEET,'Sheet changed; inspect rather than repeat'
 d=json.loads((R/'.build/power_pre_3v3_get_schematic_layout.json').read_text())
 wires=[x['uuid'] for x in d['wires'] if max(x['x1'],x['x2'])<100 and min(x['y1'],x['y2'])>233]
 assert len(wires)==11
 refs=['U106','C110','C111','#PWR011','#PWR012','#PWR056','#PWR057']
 uuids=wires+['9134b827-bccd-497e-bcda-9cd1f98c5e7a','1a792577-0dd4-4884-b106-c72b43dddaa4','9bd81cdb-1ee8-4283-a20d-7714751e829d','bfb0b44a-fd2d-4aca-a2db-ecc5676cc03f']
 labels=json.loads((R/'.build/power_pre_3v3_list_schematic_labels.json').read_text())['labels']
 c=Client()
 try:
  call(c,'batch_delete',{'schematic':SCH,'references':refs,'uuids':uuids})
  for lab in labels:
   if lab['net']!='VLED_3V9':continue
   a={'schematic':SCH,'net':lab['net'],'x':lab['x'],'y':lab['y']};call(c,'delete_schematic_net_label',a)
   if lab['y']<233:
    call(c,'add_schematic_net_label',{**a,'net':'+3V3','rotation':lab['rotation'],'label_type':'global_label'})
  call(c,'edit_schematic_component',{'schematic':SCH,'reference':'R117','value':'56.0k 0.1%'})
  call(c,'edit_schematic_component',{'schematic':SCH,'reference':'U103','fields':{'Prototype':'Single nominal 3.3V rail. LED below-source-minimum exception accepted for prototype testing only.'},'field_placements':{'Prototype':{'hide':True}}})
  call(c,'add_schematic_text',{'schematic':SCH,'text':'Shared nominal 3.3 V rail','x':15.24,'y':146.05,'size':1.8,'bold':True})
  call(c,'add_schematic_text',{'schematic':SCH,'text':'FIRST-PROTOTYPE RAIL EXCEPTION\n56k / 10k: 3.3 V nominal. No LDO.\nPWM static estimate: 3.256 to 3.344 V.\nLED source minimum is 3.3 V.\nLED operation is NOT guaranteed.\nTest startup, low battery, Wi-Fi and\nfull-white steps at the LED pins.\nSee power.md for limits and test gates.','x':15.24,'y':241.3,'size':1.15,'justify':'left top'})
 finally:c.close()
def metadata():
 d=json.loads((R/'docs/design/power_contract.json').read_text())
 c=Client()
 try:
  for p in d['components']+d['two_terminal_support']:
   fields={'Contract':'docs/design/power_contract.json'}
   if p.get('mpn'):fields['MPN']=p['mpn']
   if p.get('value'):fields['Specification']=p['value']
   call(c,'edit_schematic_component',{'schematic':SCH,'reference':p['ref'],'fields':fields,'field_placements':{name:{'hide':True} for name in fields}})
 finally:c.close()
def check():
 c=Client()
 try:
  for n in ['list_schematic_components','list_schematic_labels','validate_component_connections','validate_wire_connections','find_shorted_nets','find_orphan_items']:
   r=call(c,n,{'schematic':SCH});(R/'.build'/('power_'+n+'.json')).write_text(json.dumps({'isError':False,'result':[r]},indent=2))
  call(c,'get_schematic_component',{'schematic':SCH,'reference':'R117'})
  call(c,'get_schematic_component',{'schematic':SCH,'reference':'J104'})
  call(c,'render_schematic_png',{'schematic':SCH,'output':str(R/'.build/power_final_reviewed.png'),'width_px':4096})
  call(c,'export_netlist',{'board':SCH,'output':str(R/'.build/power.net'),'format':'kicad'})
 finally:c.close()
if __name__=='__main__':
 {'apply':perform,'metadata':metadata,'check':check}[sys.argv[1]]()
