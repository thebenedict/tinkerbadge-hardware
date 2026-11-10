#!/usr/bin/env python3
import json
from capture_power import R,SCH,call,Client
c=Client()
try:
 cs=call(c,'list_schematic_components',{'schematic':SCH})['components']
 q=[]
 def req(n,a):q.append({'name':n,'arguments':{'schematic':SCH,**a}})
 for ref in ['R120','R121','R124','R130','D101','D102']:
  # KiCad stores field rotation relative to a quarter-turned symbol.
  req('edit_schematic_component',{'reference':ref,'field_placements':{'Reference':{'rotation':90},'Value':{'rotation':90}}})
 for x in cs:
  if x['lib_id']=='power:PWR_FLAG':req('edit_schematic_component',{'reference':x['reference'],'field_placements':{'Value':{'hide':True}}})
 req('edit_schematic_component',{'reference':'C110','field_placements':{'Value':{'x':20.32,'y':264.16}}})
 req('edit_schematic_component',{'reference':'J103','field_placements':{'Value':{'x':25.4,'y':135.89}}})
 req('edit_schematic_component',{'reference':'J102','value':'2-wire LiPo','field_placements':{'Value':{'x':383.54,'y':73.66}}})
 req('edit_schematic_component',{'reference':'J104','value':'NTC (DNP)','field_placements':{'Value':{'x':386.08,'y':133.35}}})
 req('delete_schematic_net_label',{'net':'BATT_NTC_OPTIONAL','x':391.16,'y':110.49})
 req('add_wire',{'x1':391.16,'y1':110.49,'x2':391.16,'y2':101.6})
 req('add_schematic_net_label',{'net':'BATT_NTC_OPTIONAL','x':391.16,'y':101.6,'rotation':180})
 req('delete_schematic_net_label',{'net':'CHARGER_CHG_N','x':375.92,'y':118.11})
 req('add_wire',{'x1':375.92,'y1':118.11,'x2':375.92,'y2':123.19})
 req('add_schematic_net_label',{'net':'CHARGER_CHG_N','x':375.92,'y':123.19,'rotation':0,'label_type':'global_label'})
 req('render_schematic_png',{'output':str(R/'.build/power_final.png'),'width_px':4096})
 q.append({'name':'export_netlist','arguments':{'board':SCH,'output':str(R/'.build/power.net'),'format':'kicad'}})
 q.append({'name':'run_erc','arguments':{'schematic':str(R/'tinkerbadge.kicad_sch'),'output':str(R/'.build/power_root_erc.json'),'severity':'warning'}})
 for a in q:call(c,a['name'],a['arguments'])
finally:c.close()
