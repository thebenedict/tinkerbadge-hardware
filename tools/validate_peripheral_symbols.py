#!/usr/bin/env python3
from pathlib import Path
import json,sys,time
from konnect_call import Client,unbox
root=Path(__file__).resolve().parents[1]; out=root/'.build/peripheral_cad'; scratch=Path('/private/tmp/tinkerbadge-peripheral-validation'); scratch.mkdir(exist_ok=True); sch=str(scratch/'validation.kicad_sch'); client=Client()
def call(name,**args):
 r=client.call(name,args);(out/f'{time.time_ns()}-{name}.json').write_text(json.dumps(r,indent=2));u=unbox(r)
 print(name,json.dumps(u)[:200],flush=True)
 if u['isError']:raise RuntimeError(str(u))
 return u['result'][0]
try:
 specs=json.load(open(out/'create_symbols.json')); check=[]
 for spec in specs:
  a=spec['arguments'];info=call('get_symbol_info',lib_id='Tinkerbadge_Peripherals:'+a['name'],project_dir=str(root))
  assert {p['number']:p['name'] for p in info['pins']}=={p['number']:p['name'] for p in a['pins']}
  check.append(info)
 (out/'accepted_symbol_readback.json').write_text(json.dumps(check,indent=2))
 call('create_schematic',path=sch,size='A3')
 call('register_symbol_library',nickname='Tinkerbadge_Peripherals',library_path=str(root/'peripheral_symbols.kicad_sym'),project=str(scratch),scope='project')
 comps=[]
 for i,spec in enumerate(specs):
  a=spec['arguments'];comps.append(dict(lib_id='Tinkerbadge_Peripherals:'+a['name'],x=55.88+(i%4)*96.52,y=68.58+(i//4)*96.52,reference=a['reference_prefix']+str(i+1),value=a['value'],footprint=''))
 comps += [dict(lib_id='Transistor_FET:AO3400A',x=55.88,y=238.76,reference='Q1',value='AO3400A',footprint='Package_TO_SOT_SMD:SOT-23'),dict(lib_id='Interface_Expansion:TCA9534',x=152.4,y=238.76,reference='U9',value='TCA9534PWR',footprint='Package_SO:TSSOP-16_4.4x5mm_P0.65mm')]
 result=call('batch_place_components',schematic=sch,components=comps)
 (out/'validation_place_readback.json').write_text(json.dumps(result,indent=2))
 for c in comps:
  y=c['y']-25.4
  call('edit_schematic_component',schematic=sch,reference=c['reference'],field_placements={'Reference':dict(x=c['x'],y=y,rotation=0),'Value':dict(x=c['x'],y=y+2.54,rotation=0)})
 info=call('batch_get_schematic_pin_locations',schematic=sch,references=[c['reference'] for c in comps]); (out/'validation_pin_locations.json').write_text(json.dumps(info,indent=2))
 call('render_schematic_png',schematic=sch,output=str(out/'validation.png'),width_px=4096)
finally:client.close()
