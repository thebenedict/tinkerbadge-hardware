#!/usr/bin/env python3
"""Apply the review placement with native KiCad IPC and save a per-operation journal."""
import json,time,pathlib,sys
import pcb_call as p
plan=json.loads((p.ROOT/'docs/design/pcb_placement.json').read_text());board=str(p.ROOT/'tinkerbadge.kicad_pcb');log=p.ROOT/'exports/pcb-review/placement-operations.jsonl'
c=p.k.Client()
def call(name,args):
 r=c.call(name,args)
 with log.open('a') as f:f.write(json.dumps({'time':time.time(),'tool':name,'args':args,'result':r})+'\n')
 assert not r.get('isError'),r
 return r
try:
 for i,row in enumerate([] if '--envelopes-only' in sys.argv else plan['placements']):
  if row['side']=='B.Cu':call('flip_component',{'board':board,'reference':row['reference'],'layer':'B.Cu'})
  if i%20==0: print('Side settings',i,flush=True)
 call('set_component_placements',{'board':board,'placements':[{k:r[k] for k in ['reference','x','y','rotation']} for r in plan['placements']]})
 for row in (plan['non_electrical_envelopes'][1:] if '--resume-after-panel' in sys.argv else plan['non_electrical_envelopes']):
  call('place_component',{'board':board,'footprint':row['footprint'],'reference':row['reference'],'x':row['x'],'y':row['y'],'rotation':row['rotation'],'layer':'F.Cu'})
  if row['side']=='B.Cu':
   call('flip_component',{'board':board,'reference':row['reference'],'layer':'B.Cu'})
   call('set_component_placements',{'board':board,'placements':[{k:row[k] for k in ['reference','x','y','rotation']}]})
 for i,(x,y,d) in enumerate(plan['mounting_holes_mm']+plan['lanyard_holes_mm'],1):
  call('add_mounting_hole',{'board':board,'x':x,'y':y,'reference':'H'+str(i),'drill_diameter':d})
 for text,x,y,size in [('PLACEMENT REVIEW - UNROUTED',155,207,2),('170 electrical footprints / 9 unresolved interfaces',155,211,1.2),('110 x 100 mm - outline and mechanical choices provisional',155,214,1.1),('DISPLAY GLASS - FRONT',155,150.5,1.1),('BATTERY ALLOWANCE - REAR',154,163.5,1),('NFC ANTENNA RESERVE',191,190,1)]:
  call('add_board_text',{'board':board,'text':text,'x':x,'y':y,'layer':'Dwgs.User','size':size})
 call('save_project',{})
 print('Placement saved.',flush=True)
finally:c.close()
