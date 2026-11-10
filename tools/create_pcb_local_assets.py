#!/usr/bin/env python3
"""Create reviewed project footprints and explicit clearance-envelope models via Konnect.
These are geometry candidates for placement review, not manufacturing acceptance.
"""
import json,pathlib,sys,time
import konnect_call as k
ROOT=pathlib.Path(__file__).resolve().parents[1]
k.CONFIG=str(ROOT/'.build/pcb_konnect.toml')
LIB=ROOT/'Tinkerbadge.pretty'; MODELS=ROOT/'models'; LIB.mkdir(exist_ok=True); MODELS.mkdir(exist_ok=True)
LOG=ROOT/'.build/pcb-local-assets.jsonl'
def envelope(name,boxes):
 # KiCad VRML convention is 0.1 inch; convert source millimetres to that unit.
 s='#VRML V2.0 utf8\n# Datasheet-derived clearance envelope, NOT vendor component CAD.\n'
 for size,center,color,trans in boxes:
  s+='Transform { translation %s children [ Shape { appearance Appearance { material Material { diffuseColor %s transparency %s } } geometry Box { size %s } } ] }\n' % (' '.join(str(v/2.54) for v in center),' '.join(map(str,color)),trans,' '.join(str(v/2.54) for v in size))
 (MODELS/(name+'.wrl')).write_text(s)
def call(c,n,a):
 r=c.call(n,a)
 with LOG.open('a') as f:f.write(json.dumps({'tool':n,'args':a,'result':r})+'\n')
 if r.get('isError'):raise RuntimeError(k.unbox(r))
 print(n,a.get('name',a.get('footprint_path','')),flush=True)
 return r
def rect(x1,y1,x2,y2,w=.05):return {'type':'rect','start':{'x':x1,'y':y1},'end':{'x':x2,'y':y2},'stroke_width_mm':w,'fill':'none'}
def pad(n,x,y,w,h):return {'number':str(n),'type':'smd','shape':'roundrect','x':x,'y':y,'width':w,'height':h,'roundrect_rratio':.1}
if __name__=='__main__':
 c=k.Client()
 try:
  envelope('TPS63802_DLA0010A_envelope',[((2,3,.8),(0,0,.45),(.10,.11,.13),0)])
  envelope('HSMF-C165_envelope',[((1.6,.8,.5),(0,0,.25),(.5,.75,.42),.12)])
  items=[
   ('TPS63802_DLA0010A', [pad(n,-.9,(n-3)*.5,.6,.25) for n in range(1,6)]+[pad(n,.75,y,.9,.25) for n,y in [(10,-1),(9,-.5),(7,.5),(6,1)]]+[pad(8,.55,0,1.3,.25)],2,3,(-1.45,-1.75,1.45,1.75),'TPS63802_DLA0010A_envelope','TI DLA0010A p36 exact land pattern; independently reviewed. 10 pads, no EP11. Assembly process pending.'),
   ('HSMF-C165', [pad(n,x,y,.7,.4) for n,x,y in [(1,-.65,-.35),(2,-.65,.35),(3,.65,-.35),(4,.65,.35)]],1.6,.8,(-1.25,-.8,1.25,.8),'HSMF-C165_envelope','Broadcom AV02-0584EN p7 Fig8. 1 green A,2 red A,3 green K,4 red K. Cathode right.')]
  for name,pads,w,h,cy,model,desc in items:
   p=LIB/(name+'.kicad_mod')
   if p.exists():raise RuntimeError('Refuse overwrite '+str(p))
   call(c,'create_footprint',{'output':str(p),'name':name,'description':desc,'pads':pads,'body_width':w,'body_height':h,'model':{'path':'${KIPRJMOD}/models/'+model+'.wrl'}})
   call(c,'set_footprint_graphics',{'footprint_path':str(p),'selector':{'layer':'F.CrtYd'},'mode':'replace','graphics':[rect(*cy)]})
  call(c,'register_footprint_library',{'library_path':str(LIB),'nickname':'Tinkerbadge','scope':'project','project':str(ROOT/'tinkerbadge.kicad_pro')})
 finally:c.close()
