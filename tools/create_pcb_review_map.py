#!/usr/bin/env python3
"""Dimensioned functional placement map derived from the final native placement plan."""
import json,pathlib,html
root=pathlib.Path(__file__).resolve().parents[1];d=json.loads((root/'docs/design/pcb_placement.json').read_text());out=[]
S=4.4;Y=160
out.append('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="810" viewBox="0 0 1200 810"><rect width="1200" height="810" fill="#f5f7fb"/><g font-family="Helvetica,Arial,sans-serif">')
def text(x,y,t,size=14,color='#172439',anchor='start',weight='normal'):out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(t)}</text>')
def rect(x,y,w,h,fill,stroke='#334155',r=0,dash=''):out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.4" stroke-dasharray="{dash}"/>')
text(46,44,'TINKERBADGE / PLACEMENT REVIEW',28,weight='bold');text(46,74,'Unrouted proposal · 110 × 100 mm · four copper layers · human approval pending',16)
for side,X,mirror in [('FRONT',70,False),('REAR (viewed from back)',660,True)]:
 def px(x):return X+((210-x) if mirror else (x-100))*S
 def py(y):return Y+(y-100)*S
 def box(cx,cy,w,h,color,label='',dash=''):
  x=px(cx)-(w*S/2);y=py(cy)-(h*S/2);rect(x,y,w*S,h*S,color,r=3,dash=dash)
  if label:text(px(cx),py(cy)+4,label,12,'#172439','middle','bold')
 text(X,120,side,19,weight='bold');rect(X,Y,110*S,100*S,'#dbe8e2','#446456',17)
 if not mirror:
  box(118,107,18,25.5,'#94a3b8','RADIO');box(156,150.5,93.3,54.9,'#fafafa','DISPLAY GLASS')
  text(px(156),py(155),'93.3 × 54.9 mm envelope',13,'#475569','middle')
  box(103.7,130,7.4,8.6,'#94a3b8','USB')
  for row in d['placements']:
   if row['reference'] in ['D401','D402','D403']:box(row['x'],row['y'],3,3,'#e7b959')
  for row in d['placements']:
   if row['reference'] in ['D404','D405','D406','D407','D408']:box(row['x'],row['y'],3,3,'#e7b959')
  box(197,108,23,5,'#a7d8e0','IR / LIGHT')
  for ref,y in [('SW401',161),('SW402',171)]:
   box(102.1,y,4.2,3.5,'#ed9fb2');text(X-9,py(y)+4,ref,11,'#8b2448','end')
  text(px(140),py(184),'Left-edge button pair',14,'#8b2448','middle','bold')
 else:
  box(154,163.5,35,55,'#f3d894','BATTERY ALLOWANCE')
  text(px(154),py(169),'35 × 55 × 7 mm',12,'#6b4c14','middle')
  box(117,156,28,49,'#b9d3f0','POWER')
  box(184,147,20,44,'#b7dbd0');text(px(184),py(146),'DISPLAY',11,'#172439','middle','bold');text(px(184),py(150),'SUPPORT',11,'#172439','middle','bold')
  box(145,125,25,10,'#cbd5e1','I/O / TEST')
  box(151.5,116,12.7,7,'#d1bee8','SAO?','4 3')
  box(202,149,14,18,'#d1bee8','FPC?','4 3')
  box(206.5,165,5,6,'#94a3b8');text(px(198),py(166),'QWIIC',11)
  box(124,193,12,7,'#d1bee8','DOCK?','4 3')
 box(191,189.5,30,17,'#ddd2ef','NFC RESERVE','5 3')
 for x,y,diam in d['mounting_holes_mm']+d['lanyard_holes_mm']:out.append(f'<circle cx="{px(x)}" cy="{py(y)}" r="{diam*S/2}" fill="#f5f7fb" stroke="#6b7e8a"/>')
 text(X+55*S,632,'110 mm',14,'#475569','middle')
text(46,676,'Placement intent',17,weight='bold');text(46,702,'Front: display, radio, role/affinity lights, optical sensors, left-edge button pair.',14)
text(46,726,'Rear: protected battery allowance, power circuitry, display support and outward-facing Qwiic.',14)
text(46,766,'Review envelopes are not approved parts or mating definitions. No fabrication or routing release.',14,'#9a3412',weight='bold')
out.append('</g></svg>');(root/'exports/pcb-review/placement-review-map.svg').write_text('\n'.join(out))
