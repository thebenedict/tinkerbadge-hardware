#!/usr/bin/env python3
"""Apply the independent review's specific power-sheet visual corrections via MCP."""
from capture_power import R,SCH,call,Client
q=[]
def req(n,a):q.append({'name':n,'arguments':{'schematic':SCH,**a}})
def wire(x1,y1,x2,y2):req('add_wire',dict(x1=x1,y1=y1,x2=x2,y2=y2))
def relabel(net,old,new,rot=0,global_=False):
 req('delete_schematic_net_label',{'net':net,'x':old[0],'y':old[1]})
 req('add_schematic_net_label',{'net':net,'x':new[0],'y':new[1],'rotation':rot,'label_type':'global_label' if global_ else 'net_label'})
req('edit_schematic_component',{'reference':'R120','field_placements':{'Reference':{'x':300.99,'y':55.88,'rotation':90},'Value':{'x':300.99,'y':58.42,'rotation':90}}})
req('delete_schematic_net_label',{'net':'CHARGER_TMR','x':314.96,'y':63.5})
wire(314.96,63.5,287.02,63.5);wire(287.02,63.5,287.02,36.83);wire(287.02,36.83,292.1,36.83)
req('edit_schematic_component',{'reference':'J102','field_placements':{'Value':{'x':388.62,'y':55.88}}})
wire(391.16,95.25,355.6,95.25);wire(355.6,95.25,355.6,99.06)
relabel('BATT_NTC_OPTIONAL',(391.16,95.25),(355.6,99.06),180)
req('edit_schematic_component',{'reference':'U106','field_placements':{'Reference':{'x':45.72,'y':232.41},'Value':{'x':45.72,'y':234.95}}})
for ref,x in [('R121',132.08),('R124',213.36)]:req('edit_schematic_component',{'reference':ref,'field_placements':{'Value':{'x':x,'y':260.35,'rotation':90}}})
wire(88.9,182.88,88.9,175.26);relabel('VLED_3V9',(80.01,182.88),(88.9,175.26),0,True)
wire(30.48,246.38,30.48,238.76);relabel('VLED_3V9',(35.56,246.38),(30.48,238.76),180,True)
wire(369.57,171.45,369.57,163.83);relabel('+3V3_EPD',(351.79,171.45),(369.57,163.83),0,True)
req('render_schematic_png',{'output':str(R/'.build/power_final_reviewed.png'),'width_px':4096})
q.append({'name':'export_netlist','arguments':{'board':SCH,'output':str(R/'.build/power.net'),'format':'kicad'}})
c=Client()
try:
 for a in q:call(c,a['name'],a['arguments'])
finally:c.close()
