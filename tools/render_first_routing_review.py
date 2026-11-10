#!/usr/bin/env python3
"""Export native routing layers and rasterize them with an installed browser.

No CAD edits. The selected board must have filled zones and a matching project.
Use KICAD_CLI and CHROME_EXECUTABLE to override local executable defaults.
"""
from pathlib import Path
import argparse,hashlib,html,json,os,re,subprocess,tempfile

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('board',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    b=a.board.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);before=sha(b)
    cli=os.environ.get('KICAD_CLI','/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
    chrome=os.environ.get('CHROME_EXECUTABLE','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    layers={'front-copper':'F.Cu,F.SilkS,Edge.Cuts','rear-copper':'B.Cu,B.SilkS,Edge.Cuts','inner-ground-1':'In1.Cu,Edge.Cuts','inner-ground-2':'In2.Cu,Edge.Cuts'}
    for name,ls in layers.items():
        cmd=[cli,'pcb','export','svg','--layers',ls,'--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(out/(name+'.svg'))]
        # Rear is viewed from the rear. Inner plane views remain in front coordinates.
        if name=='rear-copper':cmd+=['--mirror']
        subprocess.run(cmd+[str(b)],check=True,capture_output=True,text=True)
    def svg(name,box=None):
        s=(out/(name+'.svg')).read_text();s=s[s.index('<svg'):]
        s=re.sub(r'width="[^"]+" height="[^"]+"','width="100%" height="100%"',s,count=1)
        if box:s=re.sub(r'viewBox="[^"]+"','viewBox="'+' '.join(str(n) for n in box)+'"',s,count=1)
        if box:
            name=name+'-detail-'+str(int(box[0]))+'-'+str(int(box[1]))
            (out/(name+'.svg')).write_text(s)
        return '<img src="'+html.escape(name+'.svg')+'" alt="Native PCB layer view">'
    style='*{box-sizing:border-box}body{margin:0;padding:28px;background:#e8edf2;color:#152338;font:22px Arial,sans-serif}h1{font-size:30px;margin:0 0 12px}p{margin:0 0 20px;font-size:18px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.tile{background:#101820;border-radius:8px;overflow:hidden}.tile h2{color:#dbe5f2;margin:15px 20px;font-size:22px}.view{width:100%;height:530px;padding:12px}img{display:block;width:100%;height:100%;object-fit:contain}'
    overview='<h1>First routing pass · copper review</h1><p>Native KiCad geometry · '+html.escape(before[:12])+' · incomplete routing; unresolved interfaces remain.</p><div class="grid">'
    for name,title in [('front-copper','Front copper and silkscreen'),('rear-copper','Rear copper, viewed from rear'),('inner-ground-1','Inner ground 1, front coordinates'),('inner-ground-2','Inner ground 2, front coordinates')]:
        overview+='<div class="tile"><h2>'+title+'</h2><div class="view">'+svg(name)+'</div></div>'
    overview+='</div>'
    # Native SVG origin is PCB (100,100), verified against mounting-hole centers.
    crops=[('Converter and Kelvin sense (F.Cu)',(32,43,23,17)),('Power mux / charger (F.Cu)',(62,14,30,21)),('Accessory switch and FPC reserve (F.Cu)',(88,43,20,20)),('Shared optical sensors and transmitter (F.Cu)',(27,64,30,15))]
    close='<h1>First routing pass · local circuit views</h1><p>Front copper and silkscreen; same pinned board as the overview. Faint text may be hidden by native copper.</p><div class="grid">'
    for title,box in crops:close+='<div class="tile"><h2>'+title+'</h2><div class="view">'+svg('front-copper',box)+'</div></div>'
    close+='</div>'
    with tempfile.TemporaryDirectory(prefix='badge-routing-render-') as tmp:
        for name,body in [('routing-overview',overview),('routing-closeups',close)]:
            doc=out/(name+'.html');doc.write_text('<!doctype html><meta charset="utf-8"><title>'+name+'</title><style>'+style+'</style>'+body)
            cmd=[chrome,'--headless','--disable-gpu','--hide-scrollbars','--no-first-run','--user-data-dir='+tmp,'--screenshot='+str(out/(name+'.png')),'--window-size=1800,1320','--force-device-scale-factor=1','--virtual-time-budget=1500','--run-all-compositor-stages-before-draw',doc.as_uri()]
            subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=60)
    assert sha(b)==before
    (out/'layer-render-manifest.json').write_text(json.dumps({'board_sha256':before,'native_cli_version':subprocess.check_output([cli,'version'],text=True).strip(),'rear_view':'mirrored, viewed from rear','inner_views':'front coordinates','artifacts':{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.png','.svg','.html')}},indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
