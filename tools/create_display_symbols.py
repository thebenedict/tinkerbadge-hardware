from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]; lib=str(root/'tinkerbadge.kicad_sym')
def pin(n,name,typ,x,y,a): return {'number':str(n),'name':name,'type':typ,'x':x,'y':y,'angle':a,'length':3.81}
def body(l,t,r,b):return [{'type':'rect','start':{'x':l,'y':t},'end':{'x':r,'y':b},'stroke_width_mm':0.254,'fill':'background'}]
pp=[]
for i,(n,name,typ) in enumerate([(14,'SDA/MOSI','input'),(13,'SCL/SCK','input'),(12,'CS#','input'),(11,'D/C#','input'),(10,'RES#','input'),(9,'BUSY','output'),(8,'BS1','input'),(6,'TSCL','output'),(7,'TSDA','bidirectional'),(1,'NC','no_connect'),(4,'NC','no_connect')]):pp.append(pin(n,name,typ,-15.24,19.05-i*2.54,0))
for i,(n,name,typ) in enumerate([(2,'GDR','output'),(3,'RESE','input'),(5,'VSH2','passive'),(18,'VDD_1V8','passive'),(19,'VPP','passive'),(20,'VSH1','passive'),(21,'VGH','passive'),(22,'VSL','passive'),(23,'VGL','passive'),(24,'VCOM','passive')]):pp.append(pin(n,name,typ,15.24,19.05-i*2.54,180))
pp += [pin(15,'VDDIO','power_in',-2.54,34.29,270),pin(16,'VCI','power_in',2.54,34.29,270),pin(17,'VSS','power_in',0,-13.97,90)]
pins=[]
for i in range(8):
 pins += [pin(i+2,'A'+str(i+1),'input',-13.97,10.16-i*2.54,0),pin(18-i,'Y'+str(i+1),'tri_state',13.97,10.16-i*2.54,180)]
pins += [pin(1,'OE1#','input',-13.97,-12.7,0),pin(19,'OE2#','input',-13.97,-15.24,0),pin(20,'VCC','power_in',0,19.05,270),pin(10,'GND','power_in',0,-22.86,90)]
calls=[{'name':'create_symbol','arguments':{'library_path':lib,'name':'ED037TC1_FPC','reference_prefix':'J','value':'ED037TC1_FPC','datasheet':'https://files.waveshare.com/upload/7/71/3.7inch_e-Paper_Specification.pdf','graphics':body(-11.43,30.48,11.43,-10.16),'pins':pp}},{'name':'create_symbol','arguments':{'library_path':lib,'name':'SN74LVC541A','reference_prefix':'U','value':'SN74LVC541APWR','datasheet':'https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf','graphics':body(-10.16,15.24,10.16,-19.05),'pins':pins}},{'name':'register_symbol_library','arguments':{'nickname':'Tinkerbadge','library_path':lib,'project':str(root/'tinkerbadge.kicad_pro'),'scope':'project'}}]
(root/'.build/create_display_symbols.json').write_text(json.dumps(calls,indent=2))
