#!/usr/bin/env python3
"""Compare exported netlists before/after a graphic-only schematic revision."""
from pathlib import Path
import argparse,json,hashlib
from check_schematic_contracts import sexp,children,val

def canonical(node):
 if not isinstance(node,list):return node
 # Named S-expression children are order-insensitive in these exported records.
 atoms=[x for x in node[1:] if not isinstance(x,list)]
 nested=[canonical(x) for x in node[1:] if isinstance(x,list)]
 return [node[0],*atoms,*sorted(nested,key=lambda x:json.dumps(x,sort_keys=True))]

def snapshot(path):
 tree=sexp(path.read_text());comps={};nets={};pins={}
 for c in children(children(tree,'components')[0],'comp'):
  ref=val(c,'ref');assert ref not in comps,('duplicate component',ref)
  comps[ref]=canonical(c)
 for n in children(children(tree,'nets')[0],'net'):
  name=val(n,'name');assert name not in nets,('duplicate net',name)
  nets[name]=sorted([canonical(x) for x in children(n,'node')],key=lambda x:json.dumps(x))
 for parent in children(tree,'libparts'):
  for part in children(parent,'libpart'):
   key=(val(part,'lib') or '')+':'+(val(part,'part') or '')
   assert key not in pins,('duplicate libpart',key)
   pins[key]=[canonical(p) for p in children(part,'pins')]
 return {'components':comps,'nets':nets,'library_pins':pins}

def compare(before,after):
 a=snapshot(before);b=snapshot(after);issues=[]
 for kind in a:
  for key in sorted(set(a[kind])|set(b[kind])):
   if a[kind].get(key)!=b[kind].get(key):issues.append({'kind':kind,'id':key,'before':a[kind].get(key),'after':b[kind].get(key)})
 return {'before':str(before),'before_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'after':str(after),'after_sha256':hashlib.sha256(after.read_bytes()).hexdigest(),'component_count':len(b['components']),'net_count':len(b['nets']),'library_part_count':len(b['library_pins']),'scope':'Every exported component record, actual named net membership/node properties and library physical-pin definitions. Export timestamps and numeric net codes are ignored.','issues':issues,'status':'PASS' if not issues else 'FAIL'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('before',type=Path);ap.add_argument('after',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args();r=compare(a.before,a.after)
 if a.output:a.output.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
