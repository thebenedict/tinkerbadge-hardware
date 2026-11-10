#!/usr/bin/env python3
"""Build a bounded, validated graphic revision from a frozen native baseline.
User-authorized direct editing; only specified graphic/text/geometry nodes change.
Unchanged native sections remain byte-for-byte unchanged. Main files are not written.
"""
from pathlib import Path
import json,re,uuid,hashlib,copy,shutil
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/outlined_blocks/baseline';OUT=ROOT/'.build/outlined_blocks/candidate'
TOKEN=re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+')
class Node(list):
 def __init__(self,start):super().__init__();self.start=start;self.end=None

def parse(text):
 stack=[];root=None
 for m in TOKEN.finditer(text):
  t=m.group()
  if t=='(':
   n=Node(m.start())
   if stack:stack[-1].append(n)
   stack.append(n)
  elif t==')':
   assert stack,'Unbalanced native file';n=stack.pop();n.end=m.end()
   if not stack:assert root is None;root=n
  else:assert stack;stack[-1].append(t)
 assert not stack and root and root[0]=='kicad_sch'
 return root

def dec(t):return json.loads(t) if t.startswith('"') else t
def ch(n,key):return [v for v in n[1:] if isinstance(v,list) and v and v[0]==key]
def one(n,key):
 a=ch(n,key);assert len(a)==1,(key,len(a));return a[0]
def value(n,key):
 a=ch(n,key);return dec(a[0][1]) if a else None
def num(v):return format(round(float(v),6),'.6f').rstrip('0').rstrip('.') or '0'
def dump(n,level=0):
 if not isinstance(n,list):return n
 if not any(isinstance(v,list) for v in n):return '('+' '.join(n)+')'
 atoms=[];nested=[];seen=False
 for v in n:
  if isinstance(v,list):seen=True;nested.append(v)
  else:assert not seen,('Unexpected mixed node order',n[0]);atoms.append(v)
 pad='  '*(level+1)
 return '('+' '.join(atoms)+'\n'+'\n'.join(pad+dump(v,level+1) for v in nested)+'\n'+'  '*level+')'
def ref(n):
 return next((dec(p[2]) for p in ch(n,'property') if dec(p[1])=='Reference'),None)
def props(n):return {dec(p[1]):p for p in ch(n,'property')}
def at(n):return [float(v) for v in one(n,'at')[1:3]]
def setat(n,x,y):a=one(n,'at');a[1:3]=[num(x),num(y)]
def move(n,dx,dy):
 if n[0]=='wire':
  for p in ch(one(n,'pts'),'xy'):p[1:3]=[num(float(p[1])+dx),num(float(p[2])+dy)]
 else:
  x,y=at(n);setat(n,x+dx,y+dy)
  for p in ch(n,'property'):
   x,y=at(p);setat(p,x+dx,y+dy)

def points(n):
 if n[0]=='wire':return [[float(p[1]),float(p[2])] for p in ch(one(n,'pts'),'xy')]
 if ch(n,'at'):return [at(n)]
 return []

def semantic(n):
 n=copy.deepcopy(n)
 if n[0]=='symbol':
  n[:]=[p for p in n if not(isinstance(p,list) and p[0]=='at')]
  for p in ch(n,'property'):p[:]=[v for v in p if not(isinstance(v,list) and v[0] in ('at','effects'))]
 elif n[0]=='wire':n[:]=[p for p in n if not(isinstance(p,list) and p[0]=='pts')]
 elif n[0] in ('junction','label','global_label','no_connect'):
  n[:]=[p for p in n if not(isinstance(p,list) and p[0]=='at')]
  for p in ch(n,'property'):p[:]=[v for v in p if not(isinstance(v,list) and v[0]=='at')]
 return n

ALL_FRAMES={
'power':[
 ('USB / dock inputs',[17.78,21.59,132.08,139.70],[17.78,20.32]),
 ('USB-priority source selection',[135.89,21.59,276.86,139.70],[135.89,20.32]),
 ('Power path: charging disabled',[281.94,21.59,401.32,139.70],[281.94,20.32]),
 ('Shared nominal 3.3 V rail',[17.78,148.59,137.16,261.62],[17.78,147.32]),
 ('Battery ADC / source presence',[140.97,148.59,276.86,279.40],[140.97,147.32]),
 ('Display power',[281.94,148.59,401.32,218.44],[281.94,147.32])],
'mcu':[
 ('ESP32-S3 Processor + Interfaces',[83.82,29.21,255.27,160.02],[83.82,27.94],'LOCAL SUPPLY'),
 ('Enable + Reset',[22.86,54.61,76.20,96.52],[22.86,53.34],'ENABLE + RESET'),
 ('Boot / Download',[22.86,102.87,76.20,132.08],[22.86,101.60],'BOOT / DOWNLOAD'),
 ('Power Test',[20.32,143.51,76.20,160.02],[20.32,142.24],'POWER TEST')],
'display':[
 ('Panel interface / 3.7-inch display',[17.78,29.21,233.68,113.03],[17.78,27.94],'DISPLAY  /  3.7-inch electrophoretic panel'),
 ('Panel boost and charge pump',[17.78,139.70,208.28,217.17],[17.78,138.43],'PANEL BOOST AND CHARGE PUMP'),
 ('Panel rail decoupling',[223.52,121.92,320.04,196.85],[223.52,120.65],'PANEL RAIL DECOUPLING'),
 ('Boot / off-state bias',[17.78,223.52,175.26,255.27],[17.78,222.25],'BOOT / OFF-STATE BIAS')],
'lighting':[
 ('Addressable RGB Chain',[17.78,27.94,400.05,124.46],[17.78,26.67],'LIGHTING AND USER INPUTS'),
 ('Independent Green / Red Power Indicator',[17.78,134.62,170.18,238.76],[17.78,132.08],'Independent green/red power indication'),
 ('User Buttons',[175.26,134.62,400.05,238.76],[175.26,132.08],'Two normally-open controls')],
'peripherals':[
 ('Ambient Light + I2C Pull-ups',[17.78,27.94,127.00,116.84],[17.78,26.67],None),
 ('Motion Sensor',[130.81,27.94,237.49,116.84],[130.81,26.67],None),
 ('Dynamic NFC Tag + Antenna',[240.03,27.94,400.05,116.84],[240.03,26.67],None),
 ('Status / Enable Expander',[17.78,124.46,182.88,212.09],[17.78,123.19],'STATUS / ENABLE EXPANDER'),
 ('Protected Accessory Rail + Qwiic / SAO',[218.44,123.19,400.05,247.65],[218.44,121.92],'CURRENT-LIMITED 3.3 V ACCESSORY RAIL'),
 ('Optional IR Transmitter',[17.78,215.90,93.98,280.00],[17.78,214.63],'OPTIONAL IR TX'),
 ('Optional IR Receiver',[100.33,215.90,217.17,280.00],[100.33,214.63],None)]}

def uuidfor(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'tinkerbadge:outline:2026-11-09:'+name))
def graphic(title,b,name):
 x1,y1,x2,y2=b
 return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.1778) (type dash) (color 230 0 255 1)) (fill (type none)) (uuid "{uuidfor(name+title)}"))'
def title_node(title,xy,name):return f'(text {json.dumps(title)} (at {xy[0]} {xy[1]} 0) (effects (font (size 1.52 1.52)) (justify left bottom)) (uuid "{uuidfor(name+title+"title")}"))'

def build(name):
 path=BASE/(name+'.kicad_sch');text=path.read_text();root=parse(text);original=copy.deepcopy(root);patches={};added=[];events=[]
 def dirty(n):patches[n.start]=(n.end,dump(n))
 def texts(prefix):return [n for n in ch(root,'text') if dec(n[1]).startswith(prefix)]
 def textmove(prefix,x=None,y=None,new=None):
  matches=texts(prefix);assert len(matches)==1,(name,prefix,len(matches));n=matches[0];a=at(n);setat(n,a[0] if x is None else x,a[1] if y is None else y)
  if new is not None:n[1]=json.dumps(new)
  dirty(n)
 def textdelete(prefix):
  matches=texts(prefix);assert len(matches)==1;patches[matches[0].start]=(matches[0].end,'')
 def propmove(reference,pname,x,y,center=False):
  n=next(n for n in ch(root,'symbol') if ref(n)==reference);p=props(n)[pname];setat(p,x,y)
  if center:
   e=one(p,'effects');e[:]=[v for v in e if not(isinstance(v,list) and v[0]=='justify')]
  dirty(n)
 def region(box,dx,dy,expected,expected_power=None):
  chosen=[]
  for n in root[1:]:
   if not isinstance(n,list) or n[0] not in ('symbol','wire','junction','label','global_label','no_connect'):continue
   ps=points(n)
   if ps and all(box[0]<=x<=box[2] and box[1]<=y<=box[3] for x,y in ps):chosen.append(n)
  actual={ref(n) for n in chosen if n[0]=='symbol' and not ref(n).startswith('#')};assert actual==set(expected),(name,box,actual,expected)
  actual_power={ref(n) for n in chosen if n[0]=='symbol' and ref(n).startswith('#')}
  if expected_power is not None:assert actual_power==set(expected_power),(name,box,actual_power,expected_power)
  for n in chosen:move(n,dx,dy);dirty(n)
  events.append({'region':box,'offset':[dx,dy],'references':sorted(actual),'nodes':len(chosen)})
 def map_points(predicate,dx,dy):
  selected=[]
  for n in root[1:]:
   if not isinstance(n,list):continue
   if n[0]=='wire':
    changed=False
    for p in ch(one(n,'pts'),'xy'):
     x,y=float(p[1]),float(p[2])
     if predicate(x,y):p[1:3]=[num(x+dx),num(y+dy)];changed=True
    if changed:dirty(n);selected.append(value(n,'uuid'))
   elif n[0] in ('symbol','junction','label','global_label','no_connect') and predicate(*at(n)):
    move(n,dx,dy);dirty(n);selected.append(value(n,'uuid'))
  events.append({'point_shift':[dx,dy],'nodes':selected})
 if name=='power':
  region([10,100,30,136],10.16,0,['J103'])
  region([60,19,105,42],0,5.08,['R101','R102'])
  region([120,220,180,283],17.78,-3.81,['Q101','R121','R122','R123'],['#PWR019','#PWR041','#PWR042'])
  region([215,220,258,283],0,-3.81,['Q102','R124','R125','R126'],['#PWR020','#PWR043','#PWR044'])
  map_points(lambda x,y:abs(x-278.13)<.001 and 68<=y<=72,7.62,0)
  textmove('FIRST-PROTOTYPE RAIL EXCEPTION',x=20.32)
  propmove('C114','Value',383.54,177.8)
  c114=next(n for n in ch(root,'symbol') if ref(n)=='C114');e=one(props(c114)['Value'],'effects');e[:]=[v for v in e if not(isinstance(v,list) and v[0]=='justify')];e.append(['justify','right']);dirty(c114)
 elif name=='display':
  region([20,225,50,255],7.62,0,['R303'])
  textdelete('03  E-PAPER DISPLAY')
  textmove('Prototype electrical capture.',17.78,20.32)
  textmove('U301 isolates',x=17.78)
  textmove('Power-on:',x=17.78)
  textmove('Use nonpolar',226.06,125.73)
 elif name=='mcu':
  textmove('02  PROCESSOR + RECOVERY',17.78,20.32)
  textmove('GPIO40 may go high',144.78,157.48)
 elif name=='lighting':
  textmove('04  LIGHTING + BUTTONS',17.78,20.32)
  for p in ['RGB chain:','Send black','Prototype gate:','Both LED control','Footprints for'] :textmove(p,x=20.32)
 elif name=='peripherals':
  textmove('05  SENSORS + EXPANSION',17.78,20.32)
  textdelete('SENSORS, NFC, ACCESSORIES AND OPTIONAL IR')
  propmove('U502','Reference',146.05,55.88);propmove('U502','Value',146.05,58.42)
  propmove('C505','Reference',223.52,35.56,True);propmove('C505','Value',223.52,38.10,True)
  propmove('C510','Reference',207.01,256.54,True);propmove('C510','Value',207.01,259.08,True)
  textmove('50 mA normal total.',220.98,128.27)
  textmove('Qwiic + SAO:',220.98,133.35)
  textmove('No hot-plug,',220.98,138.43)
  textmove('TCA9534:',20.32,209.55,new='TCA9534 address: 0x20.\nWrite latch 0x00 before\ndirection register 0xFB.')
  textmove('BH1730:',x=20.32)
  textmove('LIS2DW12:',x=133.35);textmove('CS and SA0 high.',x=133.35)
  textmove('ONBOARD I2C:',17.78,119.38)
  textmove('100 ohm /',20.32,225.43,new='100 ohm / 0.25 W\nlimits pulses.')
  map_points(lambda x,y:40<=x<=60 and abs(y-278.13)<.001,0,-3.81)
 for item in ALL_FRAMES[name]:
  title,b,xy=item[:3];old=item[3] if len(item)>3 else title
  added.append(graphic(title,b,name))
  if old is None:added.append(title_node(title,xy,name))
  else:
   matches=texts(old);assert len(matches)==1,(name,old);n=matches[0];n[1]=json.dumps(title);setat(n,*xy)
   e=one(n,'effects');font=one(e,'font');font[:]=[v for v in font if not(isinstance(v,list) and v[0] in ('bold','thickness'))];one(font,'size')[1:]=['1.52','1.52'];dirty(n)
 # Validate each existing non-graphic item retains all non-geometric tokens.
 for old,new in zip(original[1:],root[1:]):
  if isinstance(old,list) and old[0] not in ('text','rectangle'):
   assert semantic(old)==semantic(new),('Non-geometric mutation',name,old[0],value(old,'uuid'))
 patchlist=[(a,b,s) for a,(b,s) in patches.items()]+[(root.end-1,root.end-1,'\n  '+'\n  '.join(added)+'\n')]
 result=text
 for a,b,s in sorted(patchlist,reverse=True):result=result[:a]+s+result[b:]
 parsed=parse(result);ids=[value(n,'uuid') for n in parsed[1:] if isinstance(n,list) and ch(n,'uuid')];assert len(ids)==len(set(ids)),'Duplicate top-level UUID'
 assert len(ch(parsed,'rectangle'))==len(ch(original,'rectangle'))+len(ALL_FRAMES[name])
 (OUT/path.name).write_text(result)
 return {'sheet':name,'input_sha256':hashlib.sha256(text.encode()).hexdigest(),'output_sha256':hashlib.sha256(result.encode()).hexdigest(),'frames':len(ALL_FRAMES[name]),'changed_existing_nodes':len(patches),'new_nodes':len(added),'geometry_events':events,'non_geometric_tokens_preserved':True}
if __name__=='__main__':
 OUT.mkdir(exist_ok=True)
 for p in BASE.iterdir():
  if p.suffix in ('.kicad_sch','.kicad_sym','.kicad_pro') or p.name=='sym-lib-table':shutil.copy2(p,OUT/p.name)
 records=[build(name) for name in ALL_FRAMES]
 (ROOT/'.build/outlined_blocks/edit-log.json').write_text(json.dumps(records,indent=2)+'\n')
 print(json.dumps(records,indent=2))
