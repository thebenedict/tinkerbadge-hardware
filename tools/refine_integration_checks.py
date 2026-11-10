from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'tools/check_schematic_contracts.py';s=p.read_text();anchor=' refs={x[0] for x in exp}\n';insert=''' # One logical contract net must be one actual KiCad net, not disconnected
 # sheet-local labels that merely share their basename.
 named_groups={}
 for key,want in exp.items():
  if want is not None and key in actual:named_groups.setdefault(want,set()).add(actual[key])
 for want,names in sorted(named_groups.items()):
  if len(names)>1:issues.append({'expected_net':want,'error':'logical net split across actual nets','actual_nets':sorted(names)})
'''
assert anchor in s;s=s.replace(anchor,insert+anchor);p.write_text(s)
p=r/'tools/test_contract_checker.py';s=p.read_text().replace('from check_schematic_contracts import check,sexp','from check_schematic_contracts import check,sexp,children,val')
s=s.replace("print('PASS: baseline plus wrong-net, missing-lead, and missing-NC negative tests')",''' # Split one reviewed net into two local nets with the same basename.
 tree=sexp(text);nets=children(tree,'nets')[0];target=next(n for n in children(nets,'net') if val(n,'name') in ('GND','/GND'))
 node=children(target,'node')[-1];target.remove(node);nets.append(['net',['code','9999'],['name','/disconnected_sheet/GND'],node])
 def dump(x):
  import json
  return '('+' '.join(dump(y) for y in x)+')' if isinstance(x,list) else json.dumps(x)
 p.write_text(dump(tree));q=check(p,['display']);assert q['status']=='FAIL' and any(x.get('error')=='logical net split across actual nets' for x in q['issues']),q
print('PASS: baseline and four negative tests (wrong net, missing lead, missing NC, disconnected same-name net)')''');p.write_text(s)
