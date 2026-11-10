from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
from konnect_call import Client,unbox
r=Path(__file__).resolve().parents[1]; sch=str(r/'display.kicad_sch'); client=Client()
try:
 for x,y in [(96.52,41.91),(195.58,45.72),(50.8,152.4)]:
  for name,args in [('delete_schematic_net_label',dict(net='+3V3_EPD',x=x,y=y)),('add_wire',dict(x1=x,y1=y,x2=x,y2=round(y-5.08,2))),('add_junction',dict(x=x,y=y)),('add_schematic_net_label',dict(net='+3V3_EPD',x=x,y=round(y-5.08,2),label_type='global_label',rotation=0,shape='bidirectional'))]:
   if name=='delete_schematic_net_label' and x==96.52:continue # already deleted before the unknown-tool failure
   out=unbox(client.call(name,dict(schematic=sch,**args)));assert not out.get('isError'),out
   print(name,x,y)
 out=unbox(client.call('render_schematic_png',dict(schematic=sch,output=str(r/'.build/display-v2.png'),width_px=3500,inline=False)));assert not out.get('isError');print('rendered display-v2.png')
 out=unbox(client.call('export_netlist',dict(board=sch,output=str(r/'.build/display-final.net'),format='kicad')));assert not out.get('isError');print('exported display-final.net')
finally:client.close()
