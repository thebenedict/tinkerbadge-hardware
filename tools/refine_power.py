#!/usr/bin/env python3
"""Correct observed power-sheet presentation issues with precise MCP mutations."""
import json
from capture_power import R,SCH,call,Client,positions
cs=json.loads((R/'.build/power_list_schematic_components.json').read_text())['components']
labels=json.loads((R/'.build/power_list_schematic_labels.json').read_text())['labels']
ws=json.loads((R/'.build/power_list_schematic_wires.json').read_text())['wires']
q=[]
def req(n,a):q.append({'name':n,'arguments':{'schematic':SCH,**a}})
def wire(x1,y1,x2,y2):req('add_wire',dict(x1=x1,y1=y1,x2=x2,y2=y2))
def delwire(x1,y1,x2,y2):
 w=[w for w in ws if ({(round(w['x1'],3),round(w['y1'],3)),(round(w['x2'],3),round(w['y2'],3))}=={(round(x1,3),round(y1,3)),(round(x2,3),round(y2,3))})];assert len(w)==1,(x1,y1,x2,y2,w)
 req('delete_schematic_wire',{'uuid':w[0]['uuid']})
def groundref(x,y):
 match=[c for c in cs if c['lib_id']=='power:GND' and abs(c['x']-x)<.001 and abs(c['y']-y)<.001];assert len(match)==1,(x,y,match);return match[0]['reference']
def moveground(x,y,nx,ny):req('move_schematic_component',{'reference':groundref(x,y),'x':nx,'y':ny})
def oldlabel(net,x=None,y=None):
 a=[l for l in labels if l['net']==net and (x is None or abs(l['x']-x)<.001) and (y is None or abs(l['y']-y)<.001)];assert len(a)==1,(net,a);return a[0]
def dellabel(net,x=None,y=None):
 a=oldlabel(net,x,y);req('delete_schematic_net_label',{'net':net,'x':a['x'],'y':a['y']})
def label(net,x,y,rot=0,global_=False):req('add_schematic_net_label',{'net':net,'x':x,'y':y,'rotation':rot,'label_type':'global_label' if global_ else 'net_label'})
# Keep reference and value text horizontal and away from resistor bodies.
for c in cs:
 if not c['reference'].startswith('R'):continue
 x,y=c['x'],c['y']
 if c['rotation']==0:rp=(x+7.62,y-1.27);vp=(x+10.16,y+1.27)
 else:rp=(x,y-3.81);vp=(x,y+3.81)
 if c['reference']=='R130':rp=(x,y+3.81);vp=(x,y+6.35)
 req('edit_schematic_component',{'reference':c['reference'],'field_placements':{'Reference':{'x':rp[0],'y':rp[1],'rotation':0},'Value':{'x':vp[0],'y':vp[1],'rotation':0}}})
# Correct diode orientation, then reconnect exactly the same K and A nets.
for ref,x,y,net in [('D101',38.1,91.44,'USB_VBUS'),('D102',43.18,115.57,'DOCK_5V')]:
 dellabel(net,x,y+6.35);delwire(x,y+3.81,x,y+6.35);delwire(x,y-3.81,x,y-1.27)
 moveground(x,y-1.27,x,y+6.35)
 req('rotate_schematic_component',{'reference':ref,'rotation':270})
 wire(x,y+3.81,x,y+6.35)
 req('connect_to_net',{'reference':ref,'pin_number':'1','net':net,'label_type':'global_label','stub_length':2.54})
 req('edit_schematic_component',{'reference':ref,'field_placements':{'Reference':{'x':x+7.62,'y':y-1.27,'rotation':0},'Value':{'x':x+7.62,'y':y+1.27,'rotation':0}}})
# Move the dock label above the connector so it stays inside the sheet border.
dellabel('DOCK_5V',12.7,115.57);wire(12.7,115.57,12.7,104.14);label('DOCK_5V',12.7,104.14,global_=True)
for ref,x,y in [('J103',41.91,125.73),('J102',378.46,73.66),('J104',382.27,125.73)]:req('edit_schematic_component',{'reference':ref,'field_placements':{'Value':{'x':x,'y':y,'rotation':0}}})
req('edit_schematic_component',{'reference':'U105','field_placements':{'Value':{'x':111.76,'y':78.74}}})
# Remove collisions from inward-facing ground stubs.
for x,y,sy,nx,ny in [(179.07,58.42,55.88,139.7,58.42),(314.96,71.12,68.58,278.13,71.12),(210.82,176.53,173.99,220.98,176.53)]:
 delwire(x,sy,x,y);moveground(x,y,nx,ny);wire(x,sy,nx,sy);wire(nx,sy,nx,ny)
# A common ground bus for the three unused TMUX selects leaves their NC pins clear.
for y,gy in [(201.93,204.47),(209.55,212.09),(214.63,217.17)]:
 delwire(194.31,y,194.31,gy);req('delete_schematic_component',{'reference':groundref(194.31,gy)});wire(194.31,y,190.5,y)
wire(190.5,201.93,190.5,222.25);req('add_power_symbol',{'power_net':'GND','x':190.5,'y':222.25})
# Relocate named internal nodes off horizontal resistor bodies.
for net,x,y in [('USB_PRESENT_GATE',146.05,265.43),('DOCK_PRESENT_GATE',227.33,265.43)]:dellabel(net);label(net,x,y,180)
dellabel('CHARGE_DISABLE');wire(311.15,60.96,311.15,53.34);label('CHARGE_DISABLE',311.15,53.34,180)
dellabel('BAT_SENSE_ISOLATED');wire(232.41,196.85,232.41,190.5);label('BAT_SENSE_ISOLATED',232.41,190.5)
# LDO enable ties locally to its input, rather than repeating a label over C110.
dellabel('VLED_3V9',35.56,248.92);wire(35.56,246.38,35.56,248.92)
req('edit_schematic_component',{'reference':'U106','field_placements':{'Reference':{'x':45.72,'y':236.22},'Value':{'x':45.72,'y':238.76}}})
req('edit_schematic_component',{'reference':'C110','field_placements':{'Reference':{'x':20.32,'y':241.3},'Value':{'x':33.02,'y':254.0}}})
# Input power flags express that the connectors provide these external supplies and return.
for x,y,nx,ny in [(60.96,87.63,74.93,87.63),(66.04,111.76,81.28,111.76),(60.96,97.79,74.93,97.79)]:
 wire(x,y,nx,ny);req('add_power_symbol',{'power_net':'PWR_FLAG','x':nx,'y':ny})
# Text UUIDs read only to locate annotations: there is no MCP text-list tool.
req('batch_delete',{'uuids':['74ab857f-3055-40c1-903e-a874edbac0e4','0360677b-184d-4d65-b224-acca16eee4e7']})
req('add_schematic_text',{'x':281.94,'y':246.38,'text':'DEVELOPMENT SAFETY GATES\nR120 fitted: charging OFF. J104 thermistor DNP.\nFitting a sensor alone does not enable charging.\nJ102 terminal numbers are logical, not vendor polarity.\nFootprints / exact pack / thermal and peak loads: pending.\nUSB 100 mA and dock 500 mA modes need bench validation.','size':1.27})
req('render_schematic_png',{'output':str(R/'.build/power_refined.png'),'width_px':4096})
q.append({'name':'export_netlist','arguments':{'board':SCH,'output':str(R/'.build/power.net'),'format':'kicad'}})
(R/'.build/power_refine_requests.json').write_text(json.dumps(q,indent=2))
c=Client()
try:
 for a in q:call(c,a['name'],a['arguments'])
finally:c.close()
