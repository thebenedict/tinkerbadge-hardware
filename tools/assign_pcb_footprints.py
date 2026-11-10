#!/usr/bin/env python3
"""Assign source-reviewed placement candidates. Refuses replacement of any populated association."""
import json,pathlib,sys,hashlib,time
from check_schematic_contracts import sexp,children,val
import konnect_call as k
ROOT=pathlib.Path(__file__).resolve().parents[1];k.CONFIG=str(ROOT/'.build/pcb_konnect.toml')
m={}
for n in range(101,131):m['R'+str(n)]='Resistor_SMD:R_0603_1608Metric'
for n,size in {101:'0805_2012',102:'0805_2012',103:'1206_3216',104:'0603_1608',105:'0805_2012',106:'0805_2012',107:'0805_2012',108:'1210_3225',109:'1210_3225',112:'0805_2012',113:'0603_1608',114:'0805_2012',115:'0603_1608',116:'0603_1608'}.items():m['C'+str(n)]='Capacitor_SMD:C_'+size+'Metric'
m.update({'U101':'Tinkerbadge:TPS2121RUXR_Reviewed','U102':'Tinkerbadge:BQ24074RGTR_Reviewed','U103':'Tinkerbadge:TPS63802_DLA0010A_Reviewed','U104':'Package_TO_SOT_SMD:SOT-23-6','U107':'Package_SO:TSSOP-14_4.4x5mm_P0.65mm','J101':'Tinkerbadge:USB4105-GF-A_ProjectShells','D101':'Tinkerbadge:SMF6.0A','D102':'Tinkerbadge:SMF6.0A','D409':'Tinkerbadge:HSMF-C165','SW401':'Tinkerbadge:SKSCLBE010','SW402':'Tinkerbadge:SKSCLBE010','U501':'Tinkerbadge:BH1730FVC_WSOF6','U502':'Package_LGA:LGA-12_2x2mm_P0.5mm','U503':'Tinkerbadge:NT3H2111W0FHKH_XQFN8','D501':'Tinkerbadge:IR67-21C_TR8','U504':'Tinkerbadge:IRM-H638T_Reviewed','J501':'Tinkerbadge:JST_SH_SM04B_ProjectTabs'})
for n in range(101,104):m['Q'+str(n)]='Package_TO_SOT_SMD:SOT-23'
for n in range(401,409):m['D'+str(n)]='Tinkerbadge:WS2812C-2020-V6_Reviewed'
assert len(m)==72,len(m)
plan=[]
for sheet in ['power','lighting','peripherals']:
 path=ROOT/(sheet+'.kicad_sch');tree=sexp(path.read_text());comps={}
 for s in children(tree,'symbol'):
  props={q[1]:q[2] for q in children(s,'property') if len(q)>2};ref=props.get('Reference')
  if ref in m:
   assert props.get('Footprint','') in ['',m[ref]],(ref,props.get('Footprint'))
   if not props.get('Footprint'):
    comps[ref]={'reference':ref,'footprint':m[ref],'fields':{'PCB_Status':'PLACEMENT CANDIDATE; assembly and prototype gates remain open'}}
 plan.append({'schematic':str(path),'edits':list(comps.values())})
(ROOT/'docs/design/pcb_footprint_assignments.json').write_text(json.dumps({'scope':'Placement candidate associations, not procurement or assembly release','assignments':m,'passive_status':'Generic package sizing only; exact MPN, voltage derating/DC bias and assembly acceptance remain pending'},indent=2)+'\n')
if '--apply' in sys.argv:
 c=k.Client()
 try:
  for args in plan:
   if not args['edits']:continue
   r=c.call('batch_edit_schematic_components',args)
   (ROOT/'.build'/f'pcb-footprint-{time.time_ns()}.json').write_text(json.dumps({'args':args,'result':r},indent=2))
   assert not r.get('isError'),k.unbox(r)
   print(pathlib.Path(args['schematic']).name,len(args['edits']),flush=True)
 finally:c.close()
else:print('Plan ready:',sum(len(x['edits']) for x in plan),'new associations. Use --apply after exclusive schematic window is granted.')
