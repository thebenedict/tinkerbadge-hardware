#!/usr/bin/env python3
"""Task-local Konnect client for PCB operations, preserving the user's global IPC config."""
import json,pathlib,sys,time
import konnect_call as k
ROOT=pathlib.Path(__file__).resolve().parents[1]
k.CONFIG=str(ROOT/'.build/pcb_konnect.toml')
if __name__=='__main__':
 c=k.Client()
 try:
  name=sys.argv[1];args=json.loads(sys.argv[2])
  r=c.call(name,args);p=ROOT/'.build'/f'pcb-{time.time_ns()}-{name}.json';p.write_text(json.dumps(r,indent=2))
  print(json.dumps({'log':str(p),**k.unbox(r)}))
  sys.exit(2 if r.get('isError') else 0)
 finally:c.close()
