#!/usr/bin/env python3
"""Add an editable vector annotation layer to an unchanged native KiCad render.

Optical-space revision, derived from annotate_functional_blocks.py (3222240b).
No CAD write and no new component geometry. The PNG is embedded byte-for-byte.
All region coordinates come from the pinned native footprints and reviewed
component contracts. Run with Python 3.10+ and a configured Chromium browser.
"""
from __future__ import annotations
import argparse, base64, hashlib, html, json, math, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WEB=Path(os.environ.get('TINKERBADGE_WEB_SCRIPTS',str(ROOT.parent/'tinkerbadge-web/scripts'))).resolve()
sys.path.insert(0,str(WEB))
from kicad_source import child, children, prop, sexpr, sha, outline_bounds
from render_feature_views import png_channel, enclosed_holes, calibrate, source_holes

def portable_path(path):
    """Store relative evidence paths, never a workstation username."""
    return Path(os.path.relpath(Path(path).resolve(),ROOT)).as_posix()

def browser_path(requested):
    if requested:
        found=shutil.which(str(requested)) or str(Path(requested).expanduser())
        if not Path(found).is_file():raise RuntimeError('Configured Chromium executable does not exist')
        return Path(found)
    for name in ['chromium','chromium-browser','google-chrome','chrome-headless-shell']:
        found=shutil.which(name)
        if found:return Path(found)
    mac=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    if mac.is_file():return mac
    raise RuntimeError('Set CHROME_EXECUTABLE or pass --browser with a Chromium-compatible executable')

def refs(prefix, first, last): return [prefix+str(i) for i in range(first,last+1)]
def hull(points):
    points=sorted(set(points))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];hi=[]
    for p in points:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
        lo.append(p)
    for p in reversed(points):
        while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
        hi.append(p)
    return lo[:-1]+hi[:-1]

def points(fp):
    at=child(fp,'at');x,y=map(float,at[1:3]);a=math.radians(float(at[3]) if len(at)>3 else 0)
    local=[]
    layer='F.Fab' if prop(fp).get('Reference')=='U201' else 'F.CrtYd'
    # The module courtyard includes a very large RF keepout. Its native
    # fabrication outline is the component body, which is what this map labels.
    for shape in fp:
        if not isinstance(shape,list) or child(shape,'layer')!=['layer',layer]:continue
        if shape[0] in ('fp_rect','fp_line','fp_arc'):
            for key in ('start','end','mid'):
                p=child(shape,key)
                if p:local.append(tuple(map(float,p[1:3])))
            if shape[0]=='fp_rect':
                s=child(shape,'start');e=child(shape,'end');local.extend([(float(s[1]),float(e[2])),(float(e[1]),float(s[2]))])
        elif shape[0]=='fp_poly':local.extend(tuple(map(float,p[1:3])) for p in children(child(shape,'pts',[]),'xy'))
        elif shape[0]=='fp_circle':
            c=child(shape,'center');e=child(shape,'end');cx,cy=map(float,c[1:3]);rad=math.dist((cx,cy),tuple(map(float,e[1:3])))
            local.extend((cx+rad*math.cos(t*math.pi/16),cy+rad*math.sin(t*math.pi/16)) for t in range(32))
    if not local:raise RuntimeError('Missing native front courtyard: '+prop(fp).get('Reference',''))
    return [(x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)) for u,v in local]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',type=Path,required=True);ap.add_argument('--render',type=Path,required=True);ap.add_argument('--sha256',required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--draft',action='store_true');ap.add_argument('--rasterize',action='store_true');ap.add_argument('--browser',default=os.environ.get('CHROME_EXECUTABLE'),help='Chromium executable path or command; defaults to CHROME_EXECUTABLE, PATH or standard macOS Chrome');args=ap.parse_args()
    if sha(args.board)!=args.sha256:raise RuntimeError('Board hash is not the pinned revision')
    board_bytes=args.board.read_bytes();render_bytes=args.render.read_bytes();root=sexpr(board_bytes.decode());fps={prop(f)['Reference']:f for f in children(root,'footprint')}
    width,height,alpha=png_channel(args.render)
    regions=enclosed_holes(width,height,alpha,threshold=5,min_area=120)
    fit=calibrate(source_holes(args.board),regions,'front');a,b,c,d,e,f=fit['pcbToImage']
    if abs(a-e)>.005:raise RuntimeError('Expected unmirrored top orthographic render')
    orientation=[]
    for x,y,material in [(110,103,False),(200,103,True)]:
        px,py=a*x+c,e*y+f;ix,iy=math.floor(px),math.floor(py);samples=[alpha[j*width+i] for j in range(iy-2,iy+3) for i in range(ix-2,ix+3)]
        if (min(samples)<250 if material else max(samples)>0):raise RuntimeError('Asymmetric outline orientation check failed')
        orientation.append({'pcbMm':[x,y],'material':material,'alphaRange':[min(samples),max(samples)]})
    # The original raster is used at 1:1 physical pixel scale, only translated.
    bx,by,bw,bh=outline_bounds(root);W,H=2460,1630;board_left=610;board_top=400
    ox=round(board_left-(a*bx+c));oy=round(board_top-(e*by+f))
    project=lambda p:(a*p[0]+c+ox,e*p[1]+f+oy)
    right=project((bx+bw,by))[0];bottom=project((bx,by+bh))[1]
    if not(1750<right<1900 and 1200<bottom<1380):raise RuntimeError('Unexpected render framing; inspect layout before continuing')
    blocks=[]
    def block(key,title,detail,sets,placement,routes,color='#7de0e8',reservation_refs=None,extra=None):
        polygons=[]
        for group in sets:
            pts=[p for ref in group for p in points(fps[ref])]
            padding=.1 if key in ('infrared','power') else .65
            expanded=[(x+dx,y+dy) for x,y in pts for dx in [-padding,padding] for dy in [-padding,padding]]
            polygons.append({'references':group,'pcbPolygonMm':hull(expanded)})
        reservations=[]
        for ref in reservation_refs or []:reservations.append({'reference':ref,'pcbPolygonMm':hull(points(fps[ref]))})
        blocks.append({'id':key,'title':title,'detail':detail,'polygons':polygons,'reservations':reservations,'placement':placement,'routes':routes,'color':color,'extra':extra})
    # Block membership follows reviewed contracts. Native spread groups are
    # checked below as a useful additional guard, not trusted as a schematic.
    block('mcu','Processor / radio','ESP32-S3 · Wi-Fi + Bluetooth LE',[["U201"]+refs('C',201,203)+refs('R',201,207)],(62,315),[[(490,383),'mm:110,113']],color='#86c6ff')
    block('roles','Role LEDs','Three addressable pixels',[["D401","C401"],["D402","C402"],["D403","C403"]],(1150,215),[[(1340,277),'mm:180.5,99.4','mm:180.5,100.5']],color='#e7cf84')
    block('ambient','Ambient light','BH1730 · I²C light sensor',[["U501","C501","C502"]],(850,315),[[(1080,370),'mm:145,105.9']],color='#a9d893')
    block('infrared','Infrared','Transmitter / receiver + driver',[["U504","C509","C510","R507"],["D501","Q501","R504","R505","R506"]],(1950,315),[[(1940,363),'mm:210,114.5','mm:180,114.5','mm:178,114.5']],color='#a9d893')
    block('power','USB-C + power path','Input selection + charger (charge disabled)',[["J101","U101","U102","Q101","Q103","D101"]+refs('R',101,116)+['R120','R121','R122','R123']+refs('C',101,106)],(1950,570),[[(1940,607),'mm:210.3,124']],color='#e7cf84')
    block('battery','Battery sensing','TMUX1511 · isolated voltage measurement',[["U107"]+refs('R',127,130)+['C115','C116']],(62,735),[[(490,803),'mm:108,138']],color='#e7cf84')
    block('io','I/O expander','TCA9534 · status + accessory controls',[["U506","C514","C515"]+refs('R',514,517)],(62,535),[[(490,603),'mm:105,131','mm:140.5,131','mm:144,134']],color='#b7a8e5')
    block('motion','Motion sensor','LIS2DW12 · local bypass + bulk capacitors',[["U502","C503","C504","C505"]],(1950,760),[[(1940,797),'mm:211,135.5','mm:168.5,135.5','mm:166.9,135.5']],color='#a9d893')
    block('buttons','User buttons','Two left-edge tactile switches',[["SW401","R405","R411","R412","C411"],["SW402","R406","R413","R414","C412"]],(62,955),[[(490,1023),'mm:100,150']],color='#b7a8e5')
    block('converter','3.3 V buck-boost','TPS63802 · L101 inductor reserved',[["U103","C107","C108","C109","R117","R118"]],(62,1175),[[(490,1243),'mm:105,162','mm:130,162','mm:133.1,150']],color='#e7cf84',reservation_refs=['RES_L101'])
    block('display','Display support','Signal buffer, boost network + load switch',[["U301","C303","C312"]+refs('R',303,308),["Q301","D301","D302","D303","R301","R302","C301","C302"]+refs('C',304,311),['U104','C112','C113','C114','R119']],(1950,930),[[(1940,968),'mm:192.5,140','mm:190.7,140']],color='#7de0e8',reservation_refs=['RES_L301','RES_J301'],extra='L301 inductor + FPC region reserved')
    block('expansion','Expansion / Qwiic','Switched accessory power + I²C',[["U505","C511","C512","C513"]+refs('R',508,511),["J501","R512","R513"]],(1950,1110),[[(1940,1148),'mm:210.1,159']],color='#b7a8e5')
    block('nfc','NFC tag','NTAG I²C · rear copper coil planned',[["U503","C506"]],(1950,1290),[[(1940,1328),'mm:212,165','mm:202,165','mm:195,165']],color='#a9d893',reservation_refs=['MECH_NFC'],extra='Front + inner-layer keepout retained')
    block('affinity','Affinity LEDs','Five independently controlled pixels',[["D404","C404"],["D405","C405"],["D406","C406"],["D407","C407"],["D408","C408"]],(1020,1420),[[(1200,1399),'mm:155,177.2']],color='#e7cf84')
    groups={g[1]:set(child(g,'members')[1:]) for g in children(root,'group')}
    uuids={ref:child(fp,'uuid')[1] for ref,fp in fps.items()}
    group_checks=[]
    for name,expected in [('Accelerometer',['U502','C503','C504','C505']),('Ambient-light sensor',['U501','C501','C502']),('Infrared optical group',['U504','C509','C510','R507','D501','Q501','R504','R505','R506']),('I/O expander',['U506','C514','C515']+refs('R',514,517)),('Quiet battery ADC',['U107','C115','C116']+refs('R',127,130))]:
        if name in groups:
            good=groups[name]=={uuids[r] for r in expected}
            group_checks.append({'name':name,'references':expected,'exactMatch':good})
            if not good:raise RuntimeError('Native group differs from reviewed contract: '+name)
    peripheral=json.loads((ROOT/'docs/design/peripherals_contract.json').read_text());pc={row['ref']:row for row in peripheral['components']}
    for ref,target in [('C501','U501'),('C502','U501'),('C503','U502'),('C504','U502')]:
        if target not in pc[ref]['notes']:raise RuntimeError('Source capacitor allocation changed: '+ref)
    if 'LIS' not in pc['C505']['notes']:raise RuntimeError('C505 source allocation changed')
    # Source-image clipping trims only the blank margins. Opaque native board
    # and component pixels are neither transformed nor recreated.
    out=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2460" height="1630" viewBox="0 0 2460 1630">', '<title>Tinker Badge functional blocks on the native component render</title>', '<desc>Unmodified native KiCad component-render pixels with a separate vector annotation layer. Dashed amber regions are reservations only.</desc>', '<rect width="2460" height="1630" fill="#f6f8fa"/>',f'<defs><clipPath id="native-crop"><rect x="{board_left-12}" y="{board_top-12}" width="{right-board_left+24}" height="{bottom-board_top+24}"/></clipPath></defs>',f'<g id="native-render" clip-path="url(#native-crop)"><image x="{ox:.6f}" y="{oy:.6f}" width="{width}" height="{height}" xlink:href="data:image/png;base64,{base64.b64encode(render_bytes).decode()}"/></g>','<g id="annotation-layer" font-family="Helvetica,Arial,sans-serif">']
    def text(x,y,s,size=24,fill='#435365',weight=400):out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(s)}</text>')
    text(62,84,'Tinker Badge',52,'#142d3d',700);text(62,135,'Functional blocks · native component view',30,'#365369');text(62,181,'110 × 80 mm · front-side SMT · display hidden · placement review',24)
    def polyline(pts,color,width=2.2,dash=None):
        out.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    for block in blocks:
        out.append(f'<g id="block-{block["id"]}"><title>{html.escape(block["title"])}</title>')
        for polygon in block['polygons']:
            pts=[project(p) for p in polygon['pcbPolygonMm']];polyline(pts+[pts[0]],block['color'],2.1)
        for reservation in block['reservations']:
            pts=[project(p) for p in reservation['pcbPolygonMm']];polyline(pts+[pts[0]],'#edb659',2.6,'9 7')
        for route in block['routes']:
            pts=[project(tuple(map(float,p[3:].split(',')))) if isinstance(p,str) else p for p in route]
            # End each leader exactly on its native-derived region boundary.
            target=pts[-1];candidates=[]
            for polygon in block['polygons']:
                edge=[project(p) for p in polygon['pcbPolygonMm']]
                for p,q in zip(edge,edge[1:]+edge[:1]):
                    vx,vy=q[0]-p[0],q[1]-p[1];u=max(0,min(1,((target[0]-p[0])*vx+(target[1]-p[1])*vy)/(vx*vx+vy*vy)))
                    candidates.append((p[0]+u*vx,p[1]+u*vy))
            pts[-1]=min(candidates,key=lambda p:math.dist(p,target))
            polyline(pts,'#7590a0',2.0)
            x,y=pts[-1];out.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{block["color"]}" stroke="#314a56" stroke-width="1"/>')
        x,y=block['placement'];out.append(f'<rect x="{x}" y="{y-23}" width="6" height="30" rx="3" fill="{block["color"]}"/>')
        text(x+19,y,block['title'],30,'#183747',600);text(x+19,y+37,block['detail'],21)
        if block['extra']:text(x+19,y+69,block['extra'],21,'#946218')
        out.append('</g>')
    # Top/bottom LED guide lines join only the optical row, not intervening ICs.
    polyline([project((158,99)),project((203.8,99))],'#bda46c',1.8)
    polyline([project((106,178.8)),project((204,178.8))],'#bda46c',1.8)
    out.append('<path d="M62,1533 H2395" stroke="#d9e2e8"/>')
    polyline([(63,1574),(115,1574)],'#edb659',2.6,'9 7');text(132,1582,'Dashed amber: reserved regions, no qualified component / coil',21)
    text(1455,1582,'PCB SHA-256 '+args.sha256[:16]+' · 10 Nov 2026',20)
    if args.draft:text(1980,84,'LAYOUT TEST',27,'#9b5717',600)
    out.extend(['</g>','</svg>']);args.output.parent.mkdir(parents=True,exist_ok=True);svg=args.output.with_suffix('.svg');svg.write_text('\n'.join(out))
    record={'schemaVersion':1,'board':portable_path(args.board),'boardSha256':args.sha256,'render':portable_path(args.render),'renderSha256':sha(args.render),'renderWidth':width,'renderHeight':height,'svgSha256':sha(svg),'calibration':fit,'orientationVerification':orientation,'imagePlacement':{'translatePx':[ox,oy],'scale':1,'embeddedOriginalBytes':True},'blocks':blocks,'nativeGroupChecks':group_checks,'contractHashes':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/design/peripherals_contract.json',ROOT/'docs/design/power_contract.json',ROOT/'docs/design/display_contract.json']},'helperHashes':{portable_path(WEB/p):sha(WEB/p) for p in ['kicad_source.py','render_feature_views.py']},'cadModified':False,'unannotatedRenderModified':False,'draft':args.draft}
    if args.rasterize:
        chrome=browser_path(args.browser);png=args.output.with_suffix('.png')
        proc=subprocess.run([str(chrome),'--headless','--disable-gpu','--hide-scrollbars','--disable-background-networking','--disable-extensions','--no-first-run','--disable-default-apps',f'--screenshot={png.resolve()}','--window-size=2460,1630',svg.resolve().as_uri()],capture_output=True,text=True,timeout=90)
        if proc.returncode or not png.exists():raise RuntimeError('SVG rasterization failed: '+proc.stderr[-2000:])
        record['pngSha256']=sha(png);version=subprocess.run([str(chrome),'--version'],capture_output=True,text=True,timeout=10);record['rasterizer']=(version.stdout.strip() or chrome.name)+'; SVG screenshot at 1x'
    if sha(args.board)!=args.sha256 or hashlib.sha256(render_bytes).hexdigest()!=sha(args.render):raise RuntimeError('An input changed while annotating')
    record['generatorSha256']=sha(__file__);args.output.with_suffix('.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'svg':str(svg),'png':str(args.output.with_suffix('.png')) if args.rasterize else None,'calibrationMaxResidualPx':fit['maxResidualPx'],'boardSha256':args.sha256},indent=2))
if __name__=='__main__':main()
