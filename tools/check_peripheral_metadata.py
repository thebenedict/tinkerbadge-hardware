#!/usr/bin/env python3
"""Read-only audit of exact MPN, passive ratings and population from exported netlist."""
import json,pathlib,sys,hashlib
from check_schematic_contracts import sexp,children,val
root=pathlib.Path(__file__).resolve().parents[1];net=pathlib.Path(sys.argv[1]);tree=sexp(net.read_text());actual={val(c,'ref'):c for c in children(children(tree,'components')[0],'comp')};contract=json.load(open(root/'docs/design/peripherals_contract.json'));issues=[];blanks=[];rows=[]
for c in contract['components']:
 a=actual.get(c['ref']);assert a is not None,c['ref'];props={val(p,'name'):val(p,'value') for p in children(a,'property')};fp=val(a,'footprint') or ''
 if c.get('mpn') and props.get('MPN')!=c['mpn']:issues.append([c['ref'],'MPN',c['mpn'],props.get('MPN')])
 if c.get('kind') in ('R','C') and props.get('Rating')!=c['value']:issues.append([c['ref'],'Rating',c['value'],props.get('Rating')])
 if props.get('Population')!=c.get('population','fitted'):issues.append([c['ref'],'Population',c.get('population'),props.get('Population')])
 if not fp:blanks.append(c['ref'])
 rows.append(dict(reference=c['ref'],value=val(a,'value'),MPN=props.get('MPN'),Rating=props.get('Rating'),Population=props.get('Population'),footprint=fp,footprint_status=props.get('FootprintStatus')))
result=dict(status='PASS' if not issues else 'FAIL',netlist=str(net),sha256=hashlib.sha256(net.read_bytes()).hexdigest(),components_checked=len(rows),passive_ratings_checked=sum(c.get('kind') in ('R','C') for c in contract['components']),blank_footprints=blanks,issues=issues,components=rows)
out=root/'.build/peripheral_cad/metadata_check.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='components'},indent=2));sys.exit(0 if not issues else 1)
