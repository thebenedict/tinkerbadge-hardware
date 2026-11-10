#!/usr/bin/env python3
"""Connect the reviewed display circuit via Konnect MCP, using saved queried pins."""
import json,pathlib,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).parent)); from konnect_call import Client,unbox
root=pathlib.Path(__file__).resolve().parents[1];sch=str(root/'display.kicad_sch'); cli=Client(); calls=[]; wires=[]; handled=set()
q=json.load(open(root/'.build/display_pin_locations.json')); pts={(c['reference'],p['number']):(round(p['x'],5),round(p['y'],5)) for c in q['components'] for p in c['pins']}
def pt(ref,pin): handled.add((ref,str(pin))); return pts[(ref,str(pin))]
def wire(a,b):
 if a!=b:
  assert abs(a[0]-b[0])<1e-5 or abs(a[1]-b[1])<1e-5,(a,b)
  wires.append(dict(x1=a[0],y1=a[1],x2=b[0],y2=b[1]))
def line(*coords):
 for a,b in zip(coords,coords[1:]):wire(a,b)
def add(name,**a): calls.append(dict(name=name,arguments=dict(schematic=sch,**a)))
def label(net,x,y,global_=False,rotation=0):add('add_schematic_net_label',net=net,x=x,y=y,label_type='global_label' if global_ else 'net_label',rotation=rotation,shape='bidirectional')
def gnd(x,y):add('add_power_symbol',power_net='GND',x=x,y=y)
def junction(x,y):add('add_junction',x=x,y=y)
def fields(ref,x,y):add('edit_schematic_component',reference=ref,field_placements={'Reference':dict(x=x,y=y,rotation=0),'Value':dict(x=x,y=y+2.54,rotation=0)})
# Readable, straight parallel digital interface.
for up,jp,net in [('18','14','EPD_MOSI_PANEL'),('17','13','EPD_SCK_PANEL'),('16','12','EPD_CS_N_PANEL'),('15','11','EPD_DC_PANEL'),('14','10','EPD_RST_N_PANEL')]:
 a,b=pt('U301',up),pt('J301',jp);wire(a,b);label(net,115.57,a[1])
# Buffer supply and unused inputs/enables.
line(pt('U301',20),(76.2,41.91),(106.68,41.91),pt('C312',1));label('+3V3_EPD',96.52,41.91,True)
line(pt('C312',2),(106.68,57.15));gnd(106.68,57.15)
for n in ['7','8','9','1','19']:
 a=pt('U301',n);wire(a,(57.15,a[1]))
line((57.15,78.74),(57.15,104.14));gnd(57.15,104.14)
for y in [81.28,83.82,88.9,91.44]:junction(57.15,y)
line(pt('U301',10),(76.2,104.14));gnd(76.2,104.14)
# Panel supplies and 4-wire selection.
line(pt('J301',15),(175.26,45.72),(208.28,45.72),pt('C303',1));line(pt('J301',16),(180.34,45.72));junction(180.34,45.72);label('+3V3_EPD',195.58,45.72,True)
line(pt('C303',2),(208.28,62.23));gnd(208.28,62.23)
line(pt('J301',17),(177.8,104.14));gnd(177.8,104.14)
line(pt('J301',8),(156.21,81.28),(156.21,104.14));gnd(156.21,104.14)
# Discrete panel-generated boost circuit; MOSFET G/S/D from queryback.
line(pt('L301',1),(50.8,152.4),pt('C301',1));label('+3V3_EPD',50.8,152.4,True)
line(pt('C301',2),(50.8,177.8));gnd(50.8,177.8)
line(pt('L301',2),(104.14,152.4),pt('D303',2));line((104.14,152.4),pt('Q301',3));junction(104.14,152.4)
line((104.14,165.1),pt('C302',1));junction(104.14,165.1);label('EPD_SW',106.68,152.4)
line(pt('D303',1),(146.05,152.4));label('EPD_VGH',146.05,152.4)
line(pt('C302',2),(177.8,165.1),pt('D302',1));line((152.4,165.1),pt('D301',2));junction(152.4,165.1);label('EPD_PUMP',139.7,165.1)
line(pt('D301',1),(152.4,187.96));gnd(152.4,187.96)
line(pt('D302',2),(177.8,187.96));label('EPD_VGL',177.8,187.96)
line(pt('Q301',2),pt('R301',1));label('EPD_RESE',104.14,190.5)
line(pt('R301',2),(104.14,210.82));gnd(104.14,210.82)
line(pt('Q301',1),(83.82,177.8),pt('R302',1));label('EPD_GDR',83.82,177.8)
line(pt('R302',2),(83.82,210.82));gnd(83.82,210.82)
# High-voltage reservoir capacitors; named panel outputs, nonpolar ceramics.
contract=json.load(open(root/'docs/design/display_contract.json')); cd={c['ref']:c for c in contract['components']}
for i in range(304,312):
 ref=f'C{i}';a,b=pt(ref,1),pt(ref,2);net=cd[ref]['pins'][0]['net'];line(a,(a[0],a[1]-5.08));label(net,a[0]-3.81,a[1]-5.08);line((a[0]-3.81,a[1]-5.08),(a[0],a[1]-5.08));wire(b,(b[0],151.13 if i<308 else 189.23))
for y in [151.13,189.23]:
 wire((231.14,y),(307.34,y));gnd(307.34,y)
 for x in [256.54,281.94]:junction(x,y)
# Defined defaults on upstream signal pins; CS high, reset/clock/data low.
for i in range(303,309):
 ref=f'R{i}'; a,b=pt(ref,1),pt(ref,2);net=cd[ref]['pins'][0]['net']
 if i==305:
  line(a,(a[0],247.65),(a[0]-3.81,247.65));label(net,a[0]-3.81,247.65)
  line(b,(b[0],229.87));add('add_power_symbol',power_net='+3V3',x=b[0],y=229.87)
 else:
  line(a,(a[0],229.87),(a[0]-3.81,229.87));label(net,a[0]-3.81,229.87)
  line(b,(b[0],247.65));gnd(b[0],247.65)
# Explicit NC and remaining named nets.
nc=[]
for c in contract['components']:
 for p in c['pins']:
  key=(c['ref'],p['number'])
  if key in handled:continue
  if p['net'] is None:nc.append(dict(zip(('x','y'),pts[key])))
  else:add('connect_to_net',reference=c['ref'],pin_number=p['number'],net=p['net'],label_type='global_label' if p['net'] in contract['ports'] else 'net_label',stub_length=5.08)
  handled.add(key)
assert len(handled)==sum(len(c['pins']) for c in contract['components'])
# Metadata and full exact MPN fields remain queryable.
fields('U301',76.2,33.02);fields('J301',177.8,33.02)
for ref in ['D301','D302']: fields(ref,pts[(ref,'1')][0]+6.35,175.26)
fields('L301',76.2,142.24);fields('D303',129.54,142.24);fields('C302',129.54,171.45)
add('batch_edit_schematic_components',edits=[{'reference':c['ref'],'fields':{'MPN':c.get('exact_mpn') or 'TBD: specification-level support part','Rating':c.get('rating',''),'Contract':'docs/design/display_contract.json'}} for c in contract['components']])
add('edit_schematic_component',reference='D301',datasheet=contract['sources']['diode']['url']);add('edit_schematic_component',reference='D302',datasheet=contract['sources']['diode']['url']);add('edit_schematic_component',reference='D303',datasheet=contract['sources']['diode']['url'])
notes=[(15.24,22.86,'DISPLAY  /  3.7-inch electrophoretic panel',2,True),(15.24,28.0,'Prototype electrical capture. Physical FPC mating and panel revision must be verified before layout.',1.27,False),(15.24,119.38,'U301 isolates MCU outputs when the panel supply is off (Ioff-rated). BUSY is a pulled-down input.',1.27,False),(15.24,124.46,'Power-on: hold reset low, enable +3V3_EPD, initialize, then update. Quiesce SPI and sleep the panel before power-off.',1.27,False),(15.24,137.16,'PANEL BOOST AND CHARGE PUMP',1.52,True),(223.52,119.38,'PANEL RAIL DECOUPLING',1.52,True),(223.52,124.46,'Use nonpolar X7R capacitors; verify capacitance under DC bias.',1.27,False),(223.52,208.28,'FPC pins 1 and 4 are NC per the raw-panel document.',1.27,False),(223.52,213.36,'Pin 5 is VSH2. VDD on pin 18 is local 1.8 V, not the 3.3 V input.',1.27,False),(15.24,220.98,'BOOT / OFF-STATE BIAS',1.52,True),(223.52,226.06,'Release gates: exact panel, FPC orientation, inductor saturation,',1.27,False),(223.52,231.14,'capacitor derating, measured startup/refresh/off-state waveforms.',1.27,False),(223.52,241.3,'J301 intentionally has no PCB footprint pending the mating audit.',1.27,False)]
for x,y,t,s,b in notes:add('add_schematic_text',text=t,x=x,y=y,size=s,bold=b)
calls.insert(0,dict(name='batch_add_wire',arguments=dict(schematic=sch,wires=wires)))
calls.insert(1,dict(name='batch_add_no_connect',arguments=dict(schematic=sch,positions=nc)))
(root/'.build/display_wire_plan.json').write_text(json.dumps(calls,indent=2))
try:
 for i,q in enumerate(calls):
  r=cli.call(q['name'],q['arguments']); (root/'.build'/f'mcp-display-wire-{i:03d}-{q["name"]}.json').write_text(json.dumps(r,indent=2))
  if r.get('isError'):raise RuntimeError(json.dumps(unbox(r)))
 print(f'Completed {len(calls)} MCP calls; {len(wires)} wire segments; {len(nc)} NC flags; {len(handled)} physical endpoints.')
 r=cli.call('render_schematic_png',dict(schematic=sch,output=str(root/'.build/display.png'),width_px=4096));(root/'.build/display_render_result.json').write_text(json.dumps(r,indent=2));print(json.dumps(unbox(r)))
finally:cli.close()
