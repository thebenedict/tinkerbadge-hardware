#!/usr/bin/env python3
"""Generate official Konnect calls; never writes native KiCad source directly."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
lib=str(root/'peripheral_symbols.kicad_sym')
def p(n,name,typ,x,y,a):return dict(number=str(n),name=name,type=typ,x=x,y=y,angle=a,length=3.81)
def rect(x,y):return [dict(type='rect',start=dict(x=-x,y=y),end=dict(x=x,y=-y),stroke_width_mm=0.254,fill='background')]
def line(x1,y1,x2,y2):return dict(type='line',start=dict(x=x1,y=y1),end=dict(x=x2,y=y2),stroke_width_mm=0.254)
S=[]
def sym(name,ref,pins,graphics,mpn=None,names=True):
 f=root/'docs/components'/((mpn or name).replace('/','-')+'.pins.json'); src=json.loads(f.read_text())['source']
 S.append(dict(name='create_symbol',arguments=dict(library_path=lib,name=name,reference_prefix=ref,value=mpn or name,datasheet=src['url'],show_pin_names=names,show_pin_numbers=True,graphics=graphics,pins=pins)))
sym('WS2812C-2020-V6','D',[p(3,'DI','input',-8.89,0,0),p(1,'DO','output',8.89,0,180),p(4,'VDD','power_in',0,11.43,270),p(2,'GND','power_in',0,-11.43,90)],rect(5.08,7.62))
sym('HSMF-C165','D',[p(1,'A_GREEN','passive',-16.51,2.54,0),p(2,'A_RED','passive',-16.51,-2.54,0),p(3,'K_GREEN','passive',16.51,2.54,180),p(4,'K_RED','passive',16.51,-2.54,180)],rect(12.7,5.08))
sym('BH1730FVC','U',[p(6,'SCL','input',-13.97,2.54,0),p(4,'SDA','bidirectional',-13.97,-2.54,0),p(2,'INT','open_collector',13.97,0,180),p(1,'VCC','power_in',-2.54,11.43,270),p(5,'DVI','power_in',2.54,11.43,270),p(3,'GND','power_in',0,-11.43,90)],rect(10.16,7.62))
sym('LIS2DW12TR','U',[p(1,'SCL/SPC','input',-16.51,7.62,0),p(4,'SDA/SDI/SDO','bidirectional',-16.51,2.54,0),p(2,'CS','input',-16.51,-2.54,0),p(3,'SDO/SA0','bidirectional',-16.51,-7.62,0),p(12,'INT1','output',16.51,7.62,180),p(11,'INT2','output',16.51,2.54,180),p(5,'NC','passive',16.51,-7.62,180),p(9,'VDD','power_in',-3.81,19.05,270),p(10,'VDD_IO','power_in',3.81,19.05,270),p(6,'GND','power_in',-5.08,-19.05,90),p(7,'RES','passive',0,-19.05,90),p(8,'GND','power_in',5.08,-19.05,90)],rect(12.7,15.24))
sym('NT3H2111W0FHKH','U',[p(3,'SCL','input',-13.97,5.08,0),p(5,'SDA','bidirectional',-13.97,0,0),p(4,'FD','open_collector',-13.97,-5.08,0),p(1,'LA','passive',13.97,5.08,180),p(8,'LB','passive',13.97,0,180),p(7,'VOUT','power_out',13.97,-5.08,180),p(6,'VCC','power_in',0,13.97,270),p(2,'VSS','power_in',0,-13.97,90)],rect(10.16,10.16))
g=[dict(type='poly',points=[dict(x=-1.27,y=1.27),dict(x=-1.27,y=-1.27),dict(x=1.27,y=0),dict(x=-1.27,y=1.27)],stroke_width_mm=0.254,fill='none'),line(1.27,-1.27,1.27,1.27),line(-0.76,1.9,0.76,3.43),line(0.76,3.43,0.0,3.43),line(0.76,3.43,0.76,2.67),line(0.76,1.9,2.29,3.43),line(2.29,3.43,1.52,3.43),line(2.29,3.43,2.29,2.67)]
sym('IR67-21C_TR8','D',[p(1,'ANODE','passive',-5.08,0,0),p(2,'CATHODE','passive',5.08,0,180)],g,'IR67-21C/TR8',False)
sym('IRM-H638T_TR2','U',[p(3,'OUT','output',13.97,0,180),p(4,'VCC','power_in',0,11.43,270),p(1,'GND','power_in',-3.81,-11.43,90),p(2,'GND','power_in',3.81,-11.43,90)],rect(10.16,7.62),'IRM-H638T/TR2')
sym('TPS2553DBVR','U',[p(1,'IN','power_in',-13.97,5.08,0),p(3,'EN','input',-13.97,0,0),p(5,'ILIM','passive',-13.97,-5.08,0),p(6,'OUT','power_out',13.97,5.08,180),p(4,'FAULT_N','open_collector',13.97,-5.08,180),p(2,'GND','power_in',0,-13.97,90)],rect(10.16,10.16))
(root/'.build/peripheral_cad/create_symbols.json').write_text(json.dumps(S,indent=2))
print('Prepared',len(S),'exact-part custom symbols')
