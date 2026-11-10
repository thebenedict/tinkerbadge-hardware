#!/usr/bin/env python3
"""Small functional review diagram, not a substitute for native assembly geometry."""
import pathlib,json,html
r=pathlib.Path(__file__).resolve().parents[1]
d=json.loads((r/'docs/design/pcb_placement.json').read_text())
assert d['board_mm']==[110,80]
assert not d.get('native_functional_groups'), 'Historical first-80mm map only; use the current functional-blocks annotation generator for organized revisions.'
rows={x['reference']:x for x in d['placements']+d['non_electrical_envelopes']}
o=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="840" viewBox="0 0 1280 840">','<rect width="1280" height="840" fill="#f7f8fb"/>','<g font-family="Helvetica,Arial,sans-serif">']
def txt(x,y,s,size=14,col='#1d3045',anchor='start',weight='normal'):
 o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{col}">{html.escape(s)}</text>')
txt(42,42,'TINKERBADGE · COMPACT PLACEMENT REVIEW',28,weight='bold')
txt(42,72,'110 × 80 mm · front-side SMT · 4.5 mm proposed display lift · unrouted',17)
txt(42,99,'Experimental RF packaging. Human placement review and unresolved interface qualification remain required.',15,'#a34d16')
for X,mirror,title in [(62,False,'FRONT · viewed facing the badge'),(708,True,'REAR · viewed from the wearer')]:
 S=4.55;Y=166
 def px(x):return X+((210-x) if mirror else (x-100))*S
 def py(y):return Y+(y-100)*S
 txt(X,140,title,18,weight='bold')
 # Polyline presents the actual notch envelope; radii omitted only in this functional map.
 pts=[(104,100),(105,100),(105,106.75),(155,106.75),(155,100),(206,100),(210,104),(210,176),(206,180),(104,180),(100,176),(100,104)]
 o.append('<polygon points="'+' '.join(f'{px(x)},{py(y)}' for x,y in pts)+'" fill="#dfece5" stroke="#3b5f50" stroke-width="2"/>')
 def box(cx,cy,w,h,col,label='',dash='',stroke='#718393',alpha=1):
  o.append(f'<rect x="{px(cx)-w*S/2}" y="{py(cy)-h*S/2}" width="{w*S}" height="{h*S}" fill="{col}" fill-opacity="{alpha}" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="{dash}"/>')
  if label:txt(px(cx),py(cy)+4,label,12,anchor='middle',weight='bold')
 if not mirror:
  box(130,113.25,18,25.5,'#9da9b5','ESP32')
  box(181,126.5,38,23,'#bdd4ec','POWER',alpha=.8)
  box(174,151,43,26,'#b2d9ca','DISPLAY SUPPORT',alpha=.8)
  box(145,128,23,18,'#d4d1e3','I/O / ADC',alpha=.8)
  box(194,161.5,17,7,'#e2cde5','NFC / I²C')
  box(202,145,14,18,'#dfcee7','FPC?','4 3',alpha=.55)
  box(130,138,8,6,'#dfcee7','BAT?','4 3')
  # Glass is an outline here so the front component zones remain visible.
  box(156,137.45,93.3,54.9,'#ffffff','',dash='8 4',stroke='#344d64',alpha=.08)
  txt(px(156),py(144),'RAISED DISPLAY GLASS',14,'#263b51','middle','bold')
  txt(px(156),py(148),'93.3 × 54.9 mm',12,'#263b51','middle')
  for ref in ['D401','D402','D403','D404','D405','D406','D407','D408']:
   q=rows[ref];box(q['x'],q['y'],3,3,'#f3c15e')
  for ref in ['SW401','SW402']:
   q=rows[ref];box(q['x'],q['y'],4.2,3.5,'#dd95ae')
  box(206.325,126,7.35,8.64,'#8ca0b6')
  txt(px(207),py(118),'USB',12,anchor='middle',weight='bold')
  box(206.5,159,4.6,7,'#8ca0b6')
  txt(px(203),py(153),'QWIIC',10,anchor='middle')
  txt(px(188),py(104),'IR / LIGHT',11,anchor='middle')
 else:
  box(154,147.5,35,55,'#e9cd8d','BATTERY ALLOWANCE')
  txt(px(154),py(151.5),'35 × 55 × 7 mm',12,'#65491f','middle')
  box(151.5,114,12.7,7,'#ccb8de','SAO?','4 3')
  box(124,175,12,7,'#ccb8de','DOCK?','4 3')
  for ref in ['TP201','TP202','TP203','TP204','TP205','TP206']:
   q=rows[ref];o.append(f'<circle cx="{px(q["x"])}" cy="{py(q["y"])}" r="3.2" fill="#d8b644" stroke="#6a5a27"/>')
  txt(px(181.5),py(112),'TEST PADS',11,anchor='middle')
 box(191,172.5,18,13,'#e1d4eb','NFC?','4 3',alpha=.75)
 for x,y,diam in d['mounting_holes_mm']+d['lanyard_holes_mm']:
  o.append(f'<circle cx="{px(x)}" cy="{py(y)}" r="{diam*S/2}" fill="#f7f8fb" stroke="#687a89" stroke-width="1"/>')
 # Dimensions show the outer envelope, not the notch area.
 a=X;b=X+110*S;bottom=Y+80*S+30
 o.append(f'<path d="M{a},{bottom-5} v10 M{a},{bottom} H{b} M{b},{bottom-5} v10" stroke="#687a89" fill="none"/>')
 txt((a+b)/2,bottom+22,'110 mm',14,anchor='middle')
 if not mirror:
  xx=X-27;yy=Y+80*S
  o.append(f'<path d="M{xx-5},{Y} h10 M{xx},{Y} V{yy} M{xx-5},{yy} h10" stroke="#687a89" fill="none"/>')
  o.append(f'<text x="{xx-10}" y="{(Y+yy)/2}" transform="rotate(-90 {xx-10} {(Y+yy)/2})" text-anchor="middle" font-size="13" fill="#1d3045">80 mm</text>')
txt(42,625,'What changed',18,weight='bold')
txt(42,651,'164 non-test electrical footprints are front-side. Rear retains six bare test pads and mechanical allowances.',15)
txt(42,677,'Affinity LEDs span the full bottom at 23.5 mm pitch. Both buttons stay on the left; USB and Qwiic face right.',15)
txt(42,703,'The top notch removes FR4 under the radio antenna. Glass remains only 3.5 mm behind the antenna.',15,'#9a431d')
txt(42,729,'NFC area is only 18 × 13 mm. Its coil, display flex, exact part heights and enclosure remain unqualified.',15,'#9a431d')
txt(42,782,'Functional diagram only. Dashed shapes and “?” labels are unresolved review envelopes, not approved parts.',14,'#546274')
o.append('</g></svg>')
out=r/'exports/pcb-review/compact-one-sided/placement-zones.svg';out.write_text('\n'.join(o))
print(out)

