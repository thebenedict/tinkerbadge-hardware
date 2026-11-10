#!/usr/bin/env python3
"""Invoke the installed Konnect MCP server. Never edits native KiCad files itself."""
import argparse, json, os, pathlib, shutil, subprocess, sys, time, select
ROOT=pathlib.Path(__file__).resolve().parents[1]
def default_binary():
 # Preserve the existing KiCad 10 macOS installation when present.
 plugin=pathlib.Path.home()/'Documents/KiCad/10.0/3rdparty/plugins/com_github_mixelpixx_konnect/bin/konnect'
 return str(plugin) if plugin.is_file() else (shutil.which('konnect') or 'konnect')
def default_config():
 if sys.platform=='darwin': return pathlib.Path.home()/'Library/Application Support/konnect/codex.toml'
 return pathlib.Path(os.environ.get('XDG_CONFIG_HOME') or pathlib.Path.home()/'.config')/'konnect/codex.toml'
BIN=os.path.expanduser(os.environ.get('KONNECT_BIN') or default_binary())
CONFIG=os.path.expanduser(os.environ.get('KONNECT_CONFIG') or str(default_config()))
class Client:
 def __init__(self):
  self.p=subprocess.Popen([BIN,'--client','codex','--config',CONFIG],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
  self.id=0
  self.rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'tinkerbadge-hardware','version':'0.1'}})
  self.write({'jsonrpc':'2.0','method':'notifications/initialized'})
 def write(self,m):
  self.p.stdin.write(json.dumps(m)+'\n'); self.p.stdin.flush()
 def rpc(self,method,params):
  self.id+=1; rid=self.id
  self.write({'jsonrpc':'2.0','id':rid,'method':method,'params':params})
  deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   if not select.select([self.p.stdout],[],[],max(0,deadline-time.monotonic()))[0]: break
   line=self.p.stdout.readline()
   if not line: raise RuntimeError('MCP exited before response')
   msg=json.loads(line)
   if msg.get('id')==rid:
    if 'error' in msg: raise RuntimeError(json.dumps(msg['error']))
    return msg['result']
  raise TimeoutError('MCP outcome unknown; inspect before retrying a mutation')
 def call(self,name,args): return self.rpc('tools/call',{'name':name,'arguments':args})
 def close(self):
  self.p.terminate()
  try:self.p.wait(timeout=3)
  except subprocess.TimeoutExpired:self.p.kill()
def unbox(r):
 out=[]
 for c in r.get('content',[]):
  if c.get('type')=='text':
   try:out.append(json.loads(c['text']))
   except ValueError:out.append(c['text'])
  elif c.get('type')=='image':out.append({'type':'image','mimeType':c.get('mimeType'),'bytes_base64':len(c.get('data',''))})
 return {'isError':r.get('isError',False),'result':out}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--catalog',action='store_true'); ap.add_argument('--call'); ap.add_argument('--args',default='{}'); ap.add_argument('--batch'); opts=ap.parse_args()
 (ROOT/'.build').mkdir(parents=True,exist_ok=True)
 c=Client()
 try:
  if opts.catalog:
   r=c.rpc('tools/list',{}); p=ROOT/'.build/konnect_catalog.json';p.write_text(json.dumps(r,indent=2));print(p); print('\n'.join(t['name'] for t in r['tools']))
  else:
   calls=json.loads(pathlib.Path(opts.batch).read_text()) if opts.batch else [{'name':opts.call,'arguments':json.loads(opts.args)}]
   for q in calls:
    r=c.call(q['name'],q.get('arguments',{})); stamp=time.time_ns(); p=ROOT/'.build'/f"mcp-{stamp}-{q['name']}.json";p.write_text(json.dumps(r,indent=2)); print(json.dumps({'tool':q['name'],'log':str(p),**unbox(r)}),flush=True)
    if r.get('isError'):sys.exit(2)
 finally:c.close()
if __name__=='__main__':main()
