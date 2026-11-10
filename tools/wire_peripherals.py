#!/usr/bin/env python3
"""Wire accepted lighting/peripheral endpoint contracts through Konnect MCP."""
import json,pathlib,time,sys
from konnect_call import Client,unbox
root=pathlib.Path(__file__).resolve().parents[1];out=root/'.build/peripheral_cad';cli=Client()
contract=json.load(open(root/'docs/design/peripherals_contract.json'));cd={c['ref']:c for c in contract['components']}
global_nets=set(contract['interfaces']['mcu_required'])|set(contract['interfaces']['power_status_inputs'])|{'I2C_SDA','I2C_SCL','EXT_SDA','EXT_SCL','+3V3','GND','VLED_3V9'}
def execute(name,args,tag='wire'):
 r=cli.call(name,args);(out/f'{tag}-{time.time_ns()}-{name}.json').write_text(json.dumps(r,indent=2));u=unbox(r)
 if u['isError']:raise RuntimeError(json.dumps(u))
 v=u['result'][0]
 if isinstance(v,dict) and (v.get('errors') or v.get('failures') or v.get('success') is False or v.get('outcome',{}).get('failed',0)):raise RuntimeError(str(v))
 return v
class Sheet:
 def __init__(self,name):
  self.name=name;self.sch=str(root/(name+'.kicad_sch'));self.q=json.load(open(out/(name+'_pins.json')));self.cs={c['reference']:c for c in self.q['components']};self.pts={(c['reference'],p['number']):(round(p['x'],5),round(p['y'],5)) for c in self.q['components'] for p in c['pins']};self.handled=set();self.wires=[];self.calls=[];self.nc=[]
 def pt(self,r,p):self.handled.add((r,str(p)));return self.pts[(r,str(p))]
 def wire(self,a,b):
  a=tuple(round(v,5) for v in a);b=tuple(round(v,5) for v in b)
  if a==b:return
  assert a[0]==b[0] or a[1]==b[1],(a,b)
  self.wires.append(dict(x1=a[0],y1=a[1],x2=b[0],y2=b[1]))
 def line(self,*pts):
  for a,b in zip(pts,pts[1:]):self.wire(a,b)
 def add(self,name,**args):self.calls.append(dict(name=name,arguments=dict(schematic=self.sch,**args)))
 def label(self,n,x,y,global_=False,rotation=0):self.add('add_schematic_net_label',net=n,x=x,y=y,label_type='global_label' if global_ else 'net_label',shape='bidirectional',rotation=rotation)
 def power(self,n,x,y):self.add('add_power_symbol',power_net=n,x=x,y=y)
 def gnd(self,x,y):self.power('GND',x,y)
 def dot(self,x,y):self.add('add_junction',x=x,y=y)
 def text(self,x,y,t,size=1.27,bold=False):self.add('add_schematic_text',text=t,x=x,y=y,size=size,bold=bold)
 def fields(self,r,x,y,rot=0):self.add('edit_schematic_component',reference=r,field_placements={'Reference':dict(x=x,y=y,rotation=rot),'Value':dict(x=x,y=y+2.54,rotation=rot)})
 def finish(self):
  for r,c in self.cs.items():
   for pin,net in cd[r]['pins'].items():
    if (r,pin) in self.handled:continue
    if net is None:self.nc.append(dict(zip(('x','y'),self.pts[(r,pin)])))
    else:self.add('connect_to_net',reference=r,pin_number=pin,net=net,label_type='global_label' if net in global_nets else 'net_label',stub_length=5.08)
    self.handled.add((r,pin))
  assert len(self.handled)==sum(len(cd[r]['pins']) for r in self.cs)
  edits=[]
  for r,c in self.cs.items():
   v=cd[r];fp=next(t['footprint'] for t in json.load(open(out/(self.name+'_placement_plan.json'))) if t['reference']==r)
   edits.append(dict(reference=r,fields={'MPN':v.get('mpn','TBD: support part specification'),'Rating':v.get('value',v.get('package','')),'Population':v.get('population','fitted'),'Contract':'docs/design/peripherals_contract.json','FootprintStatus':'Assigned standard; prototype validation required' if fp else 'UNASSIGNED: physical footprint/mating release gate'}))
  
  for edit in edits:self.add('edit_schematic_component',**edit)
  self.calls.insert(0,dict(name='batch_add_wire',arguments=dict(schematic=self.sch,wires=self.wires)))
  if self.nc:self.calls.insert(1,dict(name='batch_add_no_connect',arguments=dict(schematic=self.sch,positions=self.nc)))
  (out/(self.name+'_wire_plan.json')).write_text(json.dumps(self.calls,indent=2))
  for i,q in enumerate(self.calls):execute(q['name'],q['arguments'],self.name+f'-{i:03d}')
  result=execute('render_schematic_png',dict(schematic=self.sch,output=str(out/(self.name+'.png')),width_px=4096),self.name)
  print(self.name,len(self.wires),'segments',len(self.handled),'endpoints',len(self.calls),'calls',result,flush=True)
try:
 # Move an unwired FD pullup clear of the two I2C labels, then query saved pins.
 psch=str(root/'peripherals.kicad_sch')
 execute('move_schematic_component',dict(schematic=psch,reference='R503',x=243.84,y=71.12),'placement')
 q=execute('batch_get_schematic_pin_locations',dict(schematic=psch,references=[r for r in cd if int(''.join(filter(str.isdigit,r)))>=500]),'placement');(out/'peripherals_pins.json').write_text(json.dumps(q,indent=2))
 if '--only-peripherals' not in sys.argv:
  s=Sheet('lighting')
  # One continuous power rail, a local decoupler at each package, and a direct serial chain.
  s.line((25.4,55.88),(381,55.88));s.power('+3V3',25.4,55.88)
  for i in range(8):
   d=f'D{401+i}';c=f'C{401+i}';x=s.cs[d]['component_x'];cx=s.cs[c]['component_x']
   s.line(s.pt(d,4),(x,55.88));s.dot(x,55.88)
   s.line(s.pt(c,1),(cx,55.88));s.dot(cx,55.88)
   s.line(s.pt(c,2),(cx,76.2));s.gnd(cx,76.2)
   s.line(s.pt(d,2),(x,105.41));s.gnd(x,105.41)
   s.fields(d,x,111.76);s.fields(c,cx+3.81,66.04)
   if i<7:
    a=s.pt(d,1);b=s.pt(f'D{402+i}',3);s.wire(a,b);s.label(f'RGB_LINK_{i+1}',a[0]+2.54,a[1])
  s.line(s.pt('C409',1),(25.4,55.88));s.line(s.pt('C409',2),(25.4,76.2));s.gnd(25.4,76.2)
  s.line(s.pt('R401',2),s.pt('D401',3));s.label('RGB_DIN',48.26,88.9)
  s.line(s.pt('R402',1),(48.26,88.9));s.dot(48.26,88.9);s.line(s.pt('R402',2),(48.26,115.57));s.gnd(48.26,115.57)
  s.fields('C409',29.21,64.77);s.fields('R401',36.83,78.74,90);s.fields('R402',52.07,102.87)
  # Two independent status LED dies.
  for r,p,n,x in [('R403',1,'PWR_LED_G',50.8),('R404',2,'PWR_LED_R',63.5)]:
   s.wire(s.pt(r,2),s.pt('D409',p));a=s.pt(r,1);s.wire(a,(35.56,a[1]));s.label(n,35.56,a[1],True)
   pd='R405' if r=='R403' else 'R406';s.line(s.pt(pd,1),(x,a[1]));s.dot(x,a[1]);b=s.pt(pd,2);s.line(b,(x,220.98));s.gnd(x,220.98)
  s.line(s.pt('D409',3),(127,179.07),(127,201.93));s.line(s.pt('D409',4),(127,184.15));s.dot(127,184.15);s.gnd(127,201.93)
  s.fields('D409',104.14,166.37);s.fields('R403',73.66,170.18,90);s.fields('R404',73.66,189.23,90);s.fields('R405',54.61,196.85);s.fields('R406',67.31,209.55)
  # Physical normally-open buttons, series protection and an RC on the MCU side.
  for idx,swr,sr,pu,cap,net in [(0,'SW401','R411','R412','C411','BTN_A_N'),(1,'SW402','R413','R414','C412','BTN_B_N')]:
   x=243.84+101.6*idx;gx=185.42+101.6*idx
   s.wire(s.pt(swr,1),s.pt(sr,1));s.label('BTN_'+('A' if idx==0 else 'B')+'_SW_N',205.74+101.6*idx,177.8)
   s.line(s.pt(sr,2),(x,177.8),(x+25.4,177.8));s.label(net,x+25.4,177.8,True,180)
   s.line(s.pt(pu,2),(x,177.8),s.pt(cap,1));s.dot(x,177.8)
   s.line(s.pt(pu,1),(x,148.59));s.power('+3V3',x,148.59)
   s.line(s.pt(cap,2),(x,200.66));s.gnd(x,200.66)
   s.line(s.pt(swr,3),(gx,177.8),(gx,200.66));s.gnd(gx,200.66)
   s.line(s.pt(swr,4),(gx,182.88));s.dot(gx,182.88)
   sx=205.74+101.6*idx;s.line(s.pt(swr,2),(sx,182.88),(sx,177.8));s.dot(sx,177.8)
   s.fields(swr,195.58+101.6*idx,207.01,0);s.fields(sr,217.17+101.6*idx,167.64,90);s.fields(pu,x+3.81,156.21);s.fields(cap,x+3.81,190.5)
  for x,y,t,sz,b in [(15.24,22.86,'LIGHTING AND USER INPUTS',2,True),(15.24,33.02,'RGB chain: exact WS2812C-2020-V6 on shared nominal +3V3. Below 3.3 V operation is not guaranteed.',1.27,False),(15.24,38.1,'Send black before storage. Respect the system power/current budget in firmware.',1.27,False),(15.24,132.08,'Independent green/red power indication',1.52,True),(177.8,132.08,'Two normally-open controls',1.52,True),(177.8,137.16,'A is the retained storage-wake button; B is a normal input.',1.27,False),(15.24,235,'Both LED control outputs default low. Current is limited by 2.2k per die.',1.27,False),(177.8,226.06,'100k / 100nF gives about 10 ms debounce; firmware must also debounce.',1.27,False),(15.24,250.19,'Footprints for the exact LEDs and switch are intentionally blank pending their physical pad audit.',1.27,False)]:s.text(x,y,t,sz,b)
  s.finish()
 s=Sheet('peripherals')
 # Ambient light: VCC and DVI remain on the same always-on I/O domain.
 s.line(s.pt('U501',1),(60.96,39.37),(109.22,39.37),s.pt('C502',1));s.line(s.pt('U501',5),(66.04,39.37));s.dot(66.04,39.37);s.line(s.pt('C501',1),(88.9,39.37));s.dot(88.9,39.37);s.power('+3V3',60.96,39.37)
 for r in ['C501','C502']:
  a=s.pt(r,2);s.line(a,(a[0],58.42));s.gnd(a[0],58.42)
 s.line(s.pt('U501',3),(63.5,96.52));s.gnd(63.5,96.52)
 s.line(s.pt('R501',1),(22.86,45.72),(38.1,45.72),s.pt('R502',1));s.power('+3V3',22.86,45.72)
 s.line(s.pt('R501',2),(22.86,78.74),s.pt('U501',4));s.label('I2C_SDA',22.86,78.74,True)
 s.line(s.pt('R502',2),(38.1,73.66),s.pt('U501',6));s.label('I2C_SCL',38.1,73.66,True)
 # Motion: I2C selected, address 0x19. Reserved pad 7 and optional NC5 go to ground.
 s.line(s.pt('U502',9),(171.45,33.02),(231.14,33.02),s.pt('C505',1));s.power('+3V3',171.45,33.02)
 s.line(s.pt('U502',10),(179.07,33.02));s.dot(179.07,33.02)
 for r in ['C503','C504']:
  a=s.pt(r,1);s.line(a,(a[0],33.02));s.dot(a[0],33.02)
 for r in ['C503','C504','C505']:
  a=s.pt(r,2);s.line(a,(a[0],52.07));s.gnd(a[0],52.07)
 s.line(s.pt('U502',2),(147.32,81.28),(147.32,86.36),s.pt('U502',3));s.label('+3V3',147.32,86.36,True)
 for n in [6,7,8]:
  a=s.pt('U502',n);s.line(a,(a[0],102.87))
 s.line((170.18,102.87),(200.66,102.87),(200.66,86.36),s.pt('U502',5));s.dot(175.26,102.87);s.dot(180.34,102.87);s.gnd(175.26,102.87)
 # NFC RF loop and two explicitly DNP tuning positions. VOUT is unused, not a supply tie.
 s.line(s.pt('U503',6),(287.02,39.37),(307.34,39.37),s.pt('C506',1));s.power('+3V3',287.02,39.37)
 s.line(s.pt('C506',2),(307.34,57.15));s.gnd(307.34,57.15);s.line(s.pt('U503',2),(287.02,102.87));s.gnd(287.02,102.87)
 s.line(s.pt('R503',1),(243.84,62.23));s.power('+3V3',243.84,62.23)
 s.line(s.pt('R503',2),(243.84,86.36),s.pt('U503',4));s.line((259.08,86.36),(259.08,95.25));s.dot(259.08,86.36);s.label('NFC_FD_N',259.08,95.25,True)
 s.line(s.pt('U503',1),(383.54,76.2),s.pt('AE501',1));s.label('NFC_LA',322.58,76.2)
 for r in ['C507','C508']:
  a=s.pt(r,1);s.line(a,(a[0],76.2));s.dot(a[0],76.2)
  a=s.pt(r,2);s.line(a,(a[0],100.33));s.dot(a[0],100.33)
 s.line(s.pt('U503',8),(320.04,81.28),(320.04,100.33),(386.08,100.33),s.pt('AE501',2));s.label('NFC_LB',322.58,100.33)
 # Status/enable expander. Hardware keeps the accessory supply off until initialized.
 s.line(s.pt('U506',16),(76.2,137.16),(124.46,137.16),s.pt('C515',1));s.power('+3V3',76.2,137.16);s.line(s.pt('C514',1),(101.6,137.16));s.dot(101.6,137.16)
 for r in ['C514','C515']:
  a=s.pt(r,2);s.line(a,(a[0],153.67));s.gnd(a[0],153.67)
 for n in [1,2,3]:
  a=s.pt('U506',n);s.line(a,(60.96,a[1]))
 s.line((60.96,175.26),(60.96,187.96));s.dot(60.96,177.8);s.dot(60.96,180.34);s.gnd(60.96,187.96)
 s.line(s.pt('U506',8),(76.2,207.01));s.gnd(76.2,207.01)
 for n,r in [(9,'R514'),(10,'R515'),(11,'R516'),(12,'R517')]:
  a=s.pt('U506',n);b=s.pt(r,1);s.line(a,(b[0],a[1]),b);s.label(cd[r]['pins']['1'],b[0]-10.16,a[1])
  b=s.pt(r,2);s.line(b,(b[0],207.01))
 s.line((101.6,207.01),(162.56,207.01));s.dot(121.92,207.01);s.dot(142.24,207.01);s.gnd(162.56,207.01)
 # TPS2553 active-high switch, 50 mA normal accessory budget, 155 mA fault reserve.
 s.line(s.pt('C511',1),(231.14,146.05),(259.08,146.05),(259.08,167.64),s.pt('U505',1));s.line(s.pt('C512',1),(251.46,146.05));s.dot(251.46,146.05);s.power('+3V3',231.14,146.05)
 for r in ['C511','C512']:
  a=s.pt(r,2);s.line(a,(a[0],163.83));s.gnd(a[0],163.83)
 s.line(s.pt('U505',3),(236.22,172.72),s.pt('R509',1));s.label('ACC_EN',236.22,172.72)
 s.line(s.pt('U505',5),(254,177.8),s.pt('R508',1));s.label('ACC_ILIM',254,177.8)
 for r in ['R508','R509']:
  a=s.pt(r,2);s.line(a,(a[0],207.01))
 s.line((236.22,207.01),(279.4,207.01),s.pt('U505',2));s.dot(254,207.01);s.gnd(279.4,207.01)
 s.line(s.pt('U505',6),(375.92,167.64));s.label('ACC_3V3',375.92,167.64)
 for r in ['C513','R511']:
  a=s.pt(r,1);s.line(a,(a[0],167.64));s.dot(a[0],167.64);a=s.pt(r,2);s.line(a,(a[0],198.12));s.gnd(a[0],198.12)
 s.line(s.pt('U505',4),(304.8,177.8),(304.8,203.2),(368.3,203.2),s.pt('R510',2));s.label('ACC_FAULT_N',314.96,203.2)
 s.line(s.pt('R510',1),(368.3,175.26));s.power('+3V3',368.3,175.26)
 # Optional IR transmitter: low-side FET and conservative 100 ohm pulse resistor.
 s.line(s.pt('R504',1),(58.42,213.36));s.power('+3V3',58.42,213.36);s.wire(s.pt('R504',2),s.pt('D501',1));s.label('IR_LED_A',58.42,231.14)
 s.wire(s.pt('D501',2),s.pt('Q501',3));s.label('IR_LED_K',58.42,247.65)
 s.wire(s.pt('R505',2),s.pt('Q501',1));s.line(s.pt('R506',1),(45.72,255.27));s.dot(45.72,255.27);s.label('IR_GATE',45.72,255.27)
 s.line(s.pt('Q501',2),(58.42,278.13),(45.72,278.13),s.pt('R506',2));s.gnd(58.42,278.13)
 # IR receiver shares accessory enable and has the recommended local RC filter.
 s.line(s.pt('R507',2),(210.82,228.6),s.pt('C510',1));s.line(s.pt('C509',1),(187.96,228.6));s.dot(187.96,228.6);s.line(s.pt('U504',4),(162.56,228.6));s.dot(162.56,228.6);s.label('IR_RX_3V3',167.64,228.6)
 for r in ['C509','C510']:
  a=s.pt(r,2);s.line(a,(a[0],248.92));s.gnd(a[0],248.92)
 for n in [1,2]:
  a=s.pt('U504',n);s.line(a,(a[0],270.51))
 s.line((158.75,270.51),(166.37,270.51));s.gnd(162.56,270.51);s.dot(162.56,270.51)
 # External bus pullups are on the switched rail, not the onboard I2C supply.
 s.line(s.pt('R512',1),(307.34,215.9),(330.2,215.9),s.pt('R513',1));s.label('ACC_3V3',307.34,215.9)
 # Explicit visual field positions; passive MPN/rating remains in metadata.
 for r,c in s.cs.items():
  if r.startswith(('R','C')):
   rot=90 if r in ['R505','R507'] else 0
   s.fields(r,c['component_x']+3.81,c['component_y']-1.27,rot)
 for r,x,y,rot in [('U501',63.5,30.48,0),('U502',175.26,26.67,0),('U503',287.02,30.48,0),('AE501',383.54,55.88,0),('U506',76.2,130.81,0),('U505',279.4,148.59,0),('D501',73.66,236.22,270),('Q501',64.77,252.73,0),('U504',162.56,220.98,0),('J501',279.4,226.06,0),('J502',365.76,226.06,0),('R505',31.75,247.65,90),('R507',118.11,218.44,90)]:s.fields(r,x,y,rot)
 for x,y,t,sz,b in [(15.24,20.32,'SENSORS, NFC, ACCESSORIES AND OPTIONAL IR',2,True),(15.24,109.22,'BH1730: 0x29; poll ambient light. INT unused.',1.27,False),(121.92,109.22,'LIS2DW12: 0x19; INT1 for motion event wake.',1.27,False),(121.92,114.3,'CS and SA0 high. Reserved pad 7 is grounded.',1.27,False),(243.84,109.22,'NTAG: 0x55. Center metal is NOT soldered.',1.27,False),(243.84,114.3,'Tune the PCB loop in the finished badge; tuning caps DNP.',1.27,False),(15.24,119.38,'ONBOARD I2C: 100 kHz initially. NTAG errata: STOP/START >= 50 us; guard RF edges; quiet bus for 1 ms at startup.',1.27,False),(15.24,126.0,'STATUS / ENABLE EXPANDER',1.52,True),(218.44,132.08,'CURRENT-LIMITED 3.3 V ACCESSORY RAIL',1.52,True),(218.44,137.16,'50 mA normal total. 210k / 1% sets 109-152.3 mA current limit.',1.27,False),(15.24,213.36,'TCA9534: 0x20. Write output latch 0x00 before direction 0xFB.',1.27,False),(15.24,228.6,'OPTIONAL IR TX',1.52,True),(15.24,233.68,'100 ohm / 0.25 W limits pulses.',1.0,False),(243.84,253.0,'Qwiic + SAO: 3.3 V only, 50 mA shared budget.',1.27,False),(243.84,258.08,'No hot-plug, external power or off-state GPIO drive.',1.0,False),(101.6,278.13,'IR RX shares ACC_EN. Quiesce I/O before disabling.',1.0,False)]:s.text(x,y,t,sz,b)
 s.finish()
finally:cli.close()
