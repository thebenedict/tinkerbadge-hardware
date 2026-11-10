#!/usr/bin/env python3
"""Targeted visual fixes after saved-sheet render review; native writes via MCP."""
import json,pathlib,time
from konnect_call import Client,unbox
root=pathlib.Path(__file__).resolve().parents[1];out=root/'.build/peripheral_cad';calls=[]
def add(sheet,name,**a):calls.append(dict(name=name,arguments=dict(schematic=str(root/(sheet+'.kicad_sch')),**a)))
def fields(sheet,r,x,y,rot=0):add(sheet,'edit_schematic_component',reference=r,field_placements={'Reference':dict(x=x,y=y,rotation=rot),'Value':dict(x=x,y=y+2.54,rotation=rot)})
def oldwire(sheet,a,b):add(sheet,'delete_schematic_wire',x1=a[0],y1=a[1],x2=b[0],y2=b[1])
def wires(sheet,points):add(sheet,'batch_add_wire',wires=[dict(x1=a[0],y1=a[1],x2=b[0],y2=b[1]) for a,b in zip(points,points[1:])])
def label(sheet,n,x,y,g=False,rot=0):add(sheet,'add_schematic_net_label',net=n,x=x,y=y,label_type='global_label' if g else 'net_label',rotation=rot,shape='bidirectional')
def dellabel(sheet,n,x,y):add(sheet,'delete_schematic_net_label',net=n,x=x,y=y)
for r,x in [('SW401',195.58),('SW402',297.18)]:fields('lighting',r,x,207.01,0)
for n,x,y,rot in [('VLED_3V9',25.4,55.88,180),('PWR_LED_G',35.56,179.07,180),('PWR_LED_R',35.56,184.15,180),('BTN_A_N',269.24,177.8,0),('BTN_B_N',370.84,177.8,0)]:add('lighting','rotate_schematic_label',net=n,x=x,y=y,rotation=rot)
dellabel('lighting','RGB_DIN',48.26,88.9);label('lighting','RGB_DIN',44.45,88.9)
fields('peripherals','U502',175.26,22.86);fields('peripherals','U506',76.2,127);fields('peripherals','C512',251.46,140.97)
for n,x,y in [('I2C_SDA',22.86,78.74),('I2C_SCL',38.1,73.66),('+3V3',147.32,86.36)]:add('peripherals','rotate_schematic_label',net=n,x=x,y=y,rotation=180)
# Longer local enable stub clears the neighboring charge-status global label.
dellabel('peripherals','ACC_EN',91.44,167.64);wires('peripherals',[(91.44,167.64),(116.84,167.64)]);label('peripherals','ACC_EN',116.84,167.64)
# Move the lower fault return away from the output capacitor's ground legend.
dellabel('peripherals','ACC_FAULT_N',314.96,203.2)
for a,b in [((304.8,177.8),(304.8,203.2)),((304.8,203.2),(368.3,203.2)),((368.3,203.2),(368.3,187.96))]:oldwire('peripherals',a,b)
wires('peripherals',[(304.8,177.8),(304.8,209.55),(368.3,209.55),(368.3,187.96)]);label('peripherals','ACC_FAULT_N',314.96,209.55)
dellabel('peripherals','IR_GATE',45.72,255.27);label('peripherals','IR_GATE',39.37,255.27)
# Route receiver output below its decoupling ground symbol.
dellabel('peripherals','IR_RX_N',181.61,251.46);oldwire('peripherals',(176.53,251.46),(181.61,251.46));wires('peripherals',[(176.53,251.46),(177.8,251.46),(177.8,260.35),(182.88,260.35)]);label('peripherals','IR_RX_N',182.88,260.35,True)
# Place the IR TX supply after the expander note, without a wire through its text.
oldwire('peripherals',(58.42,218.44),(58.42,213.36));oldwire('peripherals',(58.42,226.06),(58.42,233.68))
add('peripherals','move_schematic_component',reference='R504',x=58.42,y=224.79);add('peripherals','move_schematic_component',reference='#PWR028',x=58.42,y=220.98)
wires('peripherals',[(58.42,228.6),(58.42,233.68)]);fields('peripherals','R504',62.23,223.52)
# Clear Qwiic power text from the adjacent ground marker.
dellabel('peripherals','ACC_3V3',269.24,240.03);wires('peripherals',[(269.24,240.03),(254,240.03)]);label('peripherals','ACC_3V3',254,240.03,False,180)
(out/'visual_fix_plan.json').write_text(json.dumps(calls,indent=2));cli=Client()
try:
 for i,c in enumerate(calls):
  r=cli.call(c['name'],c['arguments']);(out/f'visual-fix-{i:03d}-{c["name"]}.json').write_text(json.dumps(r,indent=2));u=unbox(r);v=u['result'][0]
  if u['isError'] or isinstance(v,dict) and (v.get('errors') or v.get('failures') or v.get('success') is False):raise RuntimeError(str(u))
 for sh in ['lighting','peripherals']:
  r=cli.call('render_schematic_png',dict(schematic=str(root/(sh+'.kicad_sch')),output=str(out/(sh+'.png')),width_px=4096));(out/(sh+'_render_final.json')).write_text(json.dumps(r,indent=2));print(unbox(r))
finally:cli.close()
