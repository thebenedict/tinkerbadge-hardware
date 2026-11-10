#!/usr/bin/env python3
"""Prepare and verify selective Specctra trials; native import only to new candidates.

The initial `prepare` profile reduces only unrouted network targets and rejects
existing copper. `prepare-fixed` preserves every net/pin and protects every
prewire, suppressing held nets using an empty intersection of class-allowed
and globally active layers. `audit-fixed-ses` verifies preservation, scope,
engine settings and complete geometry ingestion. `import-fixed` transfers only
verified additions into a pristine native source copy. Full native DRC and
visual/electrical review are mandatory before adoption.
"""
import argparse, collections, copy, hashlib, json, pathlib, re

TOP = set('BTN_A_N BTN_B_N CHARGER_CHG_N CHARGER_PGOOD_N DOCK_PRESENT_N EPD_BUSY EPD_CS_N EPD_DC EPD_EN EPD_MOSI EPD_RST_N EPD_SCK EXT_SCL EXT_SDA I2C_SCL I2C_SDA IR_RX_N IR_TX MOTION_INT1 NFC_FD_N PWR_LED_G PWR_LED_R RGB_DATA SAO_GPIO1 SAO_GPIO2 USB_PRESENT_N'.split())
HIER = {
 '/02  PROCESSOR + RECOVERY/': set('BOOT_N MCU_EN STRAP45 STRAP46 UART_RX UART_TX'.split()),
 '/04  LIGHTING + BUTTONS/': set('BTN_A_SW_N BTN_B_SW_N RGB_DIN PWR_GREEN_A PWR_RED_A'.split()) | {'RGB_LINK_'+str(i) for i in range(1,8)},
 '/05  SENSORS + EXPANSION/': set('ACC_EN ACC_FAULT_N IR_GATE EXP_UNUSED_P4 EXP_UNUSED_P5 EXP_UNUSED_P6 EXP_UNUSED_P7'.split()),
 '/03  E-PAPER DISPLAY/': set('EPD_CS_N_PANEL EPD_DC_PANEL EPD_MOSI_PANEL EPD_RST_N_PANEL EPD_SCK_PANEL'.split()),
}
ALLOW = TOP | {p+n for p, ns in HIER.items() for n in ns}
LAYERS = ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']
VIA = 'Via[0-3]_600:300_um'

def sha(data): return hashlib.sha256(data).hexdigest()
def children(n, tag): return [x for x in n if isinstance(x,list) and x and x[0] == tag]
def one(n, tag):
    found=children(n,tag)
    if len(found)!=1: raise ValueError('Expected one '+tag)
    return found[0]
def walk(n):
    if isinstance(n,list):
        yield n
        for x in n: yield from walk(x)
def parse(text):
    # Specctra uniquely allows the string_quote declaration's bare quote.
    text=text.replace('(string_quote ")','(string_quote "__QUOTE__")')
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()"]+',text)
    stack=[]; roots=[]
    for token in tokens:
        if token=='(':
            n=[]
            if stack: stack[-1].append(n)
            else: roots.append(n)
            stack.append(n)
        elif token==')':
            if not stack: raise ValueError('Unbalanced DSN')
            stack.pop()
        else:
            if not stack: raise ValueError('Atom outside root')
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if stack or len(roots)!=1: raise ValueError('Unbalanced/multiple DSN roots')
    return roots[0]
def fmt(n, level=0):
    if not isinstance(n,list):
        return json.dumps(n,ensure_ascii=False) if not n or re.search(r'[\s()"\\]',n) else n
    if n==['string_quote','__QUOTE__']: return '(string_quote ")'
    if not any(isinstance(x,list) for x in n): return '('+' '.join(fmt(x) for x in n)+')'
    first=[]; rest=[]
    for x in n:
        (rest if isinstance(x,list) or rest else first).append(x)
    return '('+' '.join(fmt(x) for x in first)+''.join('\n'+'  '*(level+1)+fmt(x,level+1) for x in rest)+')'
def nets(root):
    return {n[1]:n for n in children(one(root,'network'),'net')}
def padmap(root):
    return {name: one(n,'pins')[1:] for name,n in nets(root).items()}
def count(root,tag): return sum(bool(n) and n[0]==tag for n in walk(root))
def placed_pins(root):
    images={n[1]:children(n,'pin') for n in children(one(root,'library'),'image')}
    placed={p[1]:c[1] for c in children(one(root,'placement'),'component') for p in children(c,'place')}
    return {ref+'-'+[a for a in pin if isinstance(a,str)][2] for ref,image in placed.items() for pin in images[image]}

def refuse(cond,msg):
    if not cond: raise ValueError(msg)
def prepare(src,dest,manifest):
    refuse(not dest.exists() and not manifest.exists(),'Outputs must be new')
    raw=src.read_bytes(); root=parse(raw.decode()); out=copy.deepcopy(root)
    refuse(root[0]=='pcb','Not a DSN pcb')
    refuse({x[0] for x in root if isinstance(x,list)} <= {'parser','resolution','unit','structure','placement','library','network','wiring'},'Unknown top-level scope')
    refuse(one(root,'unit')==['unit','um'],'Only um units supported')
    refuse(len(one(root,'wiring'))==1,'Prewired input unsupported: protect and independently verify existing copper first')
    structure=one(out,'structure')
    refuse(not children(structure,'plane'),'Copper planes unsupported in reduction profile')
    refuse([l[1] for l in children(structure,'layer')]==LAYERS,'Unexpected stackup')
    refuse(one(structure,'via')==['via',VIA],'Unexpected via definition')
    vs=next((x for x in children(one(out,'library'),'padstack') if x[1]==VIA),None)
    refuse(vs is not None and [s[1] for s in children(vs,'shape')]==[['circle',l,'600'] for l in LAYERS],'Via copper geometry does not match 0.6 mm through via')
    maps=padmap(root)
    physical=placed_pins(root)
    refuse({p for ps in maps.values() for p in ps} <= physical,'A network pin is absent from physical library/placement')
    refuse(len(maps)==len(children(one(root,'network'),'net')),'Duplicate net names')
    # Singleton and empty nets cannot contribute routing; still retain their pads.
    selected={name:n for name,n in nets(root).items() if name in ALLOW and len(maps[name])>1}
    refuse(bool(selected),'No selected digital nets')
    network=one(out,'network'); network[:]=['network']+[copy.deepcopy(n) for n in selected.values()]
    network.append(['class','selected_digital']+list(selected)+[['circuit',['use_via',VIA],['use_layer','F.Cu','B.Cu']],['rule',['width','200'],['clearance','150']]])
    for layer in children(structure,'layer'):
        one(layer,'type')[1]='signal' if layer[1] in ['F.Cu','B.Cu'] else 'power'
    # Keep physical geometry untouched; override only routing rules.
    for rule in list(children(structure,'rule')): structure.remove(rule)
    structure.append(['rule',['width','200'],['clearance','150'],['clearance','150',['type','smd_smd']]])
    refuse(not children(structure,'autoroute_settings'),'Existing autoroute settings need explicit review')
    structure.append(['autoroute_settings',['fanout','off'],['autoroute','on'],['postroute','off'],['vias','on']]+[['layer_rule',l,['active','on' if l in ['F.Cu','B.Cu'] else 'off'],['preferred_direction','horizontal' if l=='F.Cu' else 'vertical']] for l in LAYERS])
    # Assert independent semantic invariants before writing. Library includes all
    # original copper pad shapes AND footprint keepouts, including excluded nets.
    for tag in ['placement','library','wiring','unit','resolution','parser']:
        refuse(one(root,tag)==one(out,tag),tag+' unexpectedly changed')
    for tag in ['boundary','keepout','via','via_keepout','place_keepout']:
        refuse(children(one(root,'structure'),tag)==children(structure,tag),tag+' geometry changed')
    refuse(padmap(out)=={n:maps[n] for n in selected},'Selected pad map changed')
    emitted=fmt(out)+'\n'
    refuse(parse(emitted)==out,'DSN round-trip failed')
    # Keep the exact original placement/library bytes, not merely equivalent AST.
    # Span replace by balancing tokens while accounting for quoted strings.
    def raw_scope(text,tag):
        m=re.search(r'(?m)^  \('+re.escape(tag)+r'(?:\s|\))',text)
        refuse(m is not None,'Missing standard-export '+tag+' scope')
        start=m.start()+2; i=start; depth=0; quoted=False; escaped=False
        while i<len(text):
            c=text[i]
            if quoted:
                if escaped: escaped=False
                elif c=='\\': escaped=True
                elif c=='"': quoted=False
            elif c=='"': quoted=True
            elif c=='(': depth+=1
            elif c==')':
                depth-=1
                if depth==0: return start,i+1
            i+=1
        raise ValueError('Unbalanced raw scope')
    for tag in ['placement','library']:
        a,b=raw_scope(raw.decode(),tag); x,y=raw_scope(emitted,tag)
        emitted=emitted[:x]+raw.decode()[a:b]+emitted[y:]
    refuse(parse(emitted)==out,'Raw preservation mismatch')
    report={'source':str(src.resolve()),'source_sha256':sha(raw),'output':str(dest.resolve()),'output_sha256':sha(emitted.encode()),'profile':'unrouted selective digital network reduction','required_router_settings':{'copper_to_edge_clearance_um':500,'hole_clearance_um':250,'automatic_neckdown':False,'strict_drc':True},'selected_net_count':len(selected),'selected_nets':{n:maps[n] for n in selected},'excluded_nets':{n:p for n,p in maps.items() if n not in selected},'source_net_count':len(maps),'source_pad_count':len(placed_pins(root)),'output_pad_count':len(placed_pins(out)),'pad_definition_count':count(root,'pin'),'source_keepout_count':count(root,'keepout'),'output_keepout_count':count(out,'keepout'),'placement_unchanged':True,'library_byte_identical':True,'board_boundary_unchanged':True,'existing_wiring':0,'outer_layers_only':True,'track_width_mm':.2,'clearance_mm':.15,'via_mm':[.6,.3],'unsupported':['Prewired or plane-containing input','Native DSN is not a Konnect revision-bound import manifest','Fine-pitch shape approximations remain those of native KiCad export','Complete source pin map is retained here; excluded net declarations intentionally omitted from router input','Native DRC, pad entry, paste/via overlap, electrical and visual review remain mandatory']}
    dest.write_text(emitted); manifest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['selected_net_count','source_net_count','source_pad_count','output_pad_count','source_keepout_count','output_keepout_count']}))
def audit(ses,manifest,output):
    m=json.loads(manifest.read_text()); root=parse(ses.read_text())
    refuse(root[0]=='session','Not a Specctra session')
    selected=set(m['selected_nets']); netrows=[]; errors=[]
    for n in walk(root):
        if not n or n[0]!='net': continue
        name=n[1]; wires=children(n,'wire'); vias=children(n,'via')
        if (wires or vias) and name not in selected: errors.append('Excluded/unknown net routed: '+name)
        widths=collections.Counter(); layers=collections.Counter(); length=0
        for wire in wires:
            paths=children(wire,'path')
            if len(paths)!=1: errors.append('Unsupported wire shape on '+name); continue
            path=paths[0]; layer=path[1]; width=float(path[2]); widths[str(width)]+=1;layers[layer]+=1
            if layer not in ['F.Cu','B.Cu']: errors.append('Inner copper routed: '+name)
            # SES resolution commonly um 10, coordinates in 0.1 um units.
            scale=float(one(one(root,'routes'),'resolution')[2])
            if abs(width/scale-200)>1e-6: errors.append('Unexpected width: '+name+' '+str(width/scale))
            pts=list(zip(map(float,path[3::2]),map(float,path[4::2])))
            length+=sum(((a[0]-b[0])**2+(a[1]-b[1])**2)**.5 for a,b in zip(pts,pts[1:]))/scale/1000
        for via in vias:
            if via[1]!=VIA: errors.append('Unexpected via: '+via[1])
        if wires or vias: netrows.append({'net':name,'wires':len(wires),'vias':len(vias),'layers':dict(layers),'widths_session_units':dict(widths),'length_mm':round(length,3)})
    result={'ses':str(ses.resolve()),'ses_sha256':sha(ses.read_bytes()),'selected_net_count':len(selected),'nets_with_copper':len(netrows),'wires':sum(n['wires'] for n in netrows),'vias':sum(n['vias'] for n in netrows),'length_mm':round(sum(n['length_mm'] for n in netrows),3),'net_results':netrows,'errors':sorted(set(errors)),'scope_audit_passed':not errors,'native_drc':'not performed by this tool','connectivity_complete':'not inferred from router output'}
    refuse(not output.exists(),'Audit output must be new');output.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({k:v for k,v in result.items() if k!='net_results'}))
    if errors: raise SystemExit(2)

def copper_signatures(root, session=False):
    """Canonical 0.1 um segments/vias; DSN unit and SES resolution differ."""
    result = collections.Counter()
    if session:
        routes = one(root, 'routes')
        refuse(one(routes, 'resolution') == ['resolution', 'um', '10'], 'Unsupported SES resolution')
        rows = [(n[1], w) for n in children(one(routes, 'network_out'), 'net')
                for w in n[2:] if isinstance(w, list) and w[0] in ['wire', 'via']]
        scale = 10
    else:
        refuse(one(root, 'unit') == ['unit', 'um'], 'Unsupported DSN units')
        rows = [(one(w, 'net')[1], w) for w in one(root, 'wiring')[1:]]
        scale = 1
    for net, w in rows:
        if w[0] == 'wire':
            path = one(w, 'path')
            refuse(len(path[3:]) >= 4 and len(path[3:]) % 2 == 0, 'Invalid wire path')
            pts = [(round(float(a)*10/scale), round(float(b)*10/scale))
                   for a, b in zip(path[3::2], path[4::2])]
            result.update(('wire', net, path[1], round(float(path[2])*10/scale),
                           tuple(sorted((a, b)))) for a, b in zip(pts, pts[1:]))
        elif w[0] == 'via':
            result[('via', net, w[1], round(float(w[2])*10/scale),
                    round(float(w[3])*10/scale))] += 1
        else:
            raise ValueError('Only path wires and through vias are supported')
    return result


def placement_signature(root, session=False):
    scale = 10 if session else 1
    return {p[1]: (round(float(p[2])*10/scale), round(float(p[3])*10/scale),
                    p[4], round(float(p[5]) % 360, 6))
            for c in children(one(root, 'placement'), 'component')
            for p in children(c, 'place')}


def prepare_fixed(dsn, board, allowed_path, dest, manifest):
    """Retain all networks and copper; suppress held nets by layer intersection.

    Freerouting 2.4.1 combines class use_layer with globally active signal layers.
    Held nets can use only inactive In1.Cu, so no routing layer is available.
    CLI -inc/ignore_net_classes is GUI-only in the pinned JAR and is NOT used.
    """
    refuse(not dest.exists() and not manifest.exists(), 'Outputs must be new')
    raw = dsn.read_bytes()
    source = parse(raw.decode())
    out = copy.deepcopy(source)
    refuse(source[0] == 'pcb' and one(source, 'unit') == ['unit', 'um'], 'Expected um DSN')
    refuse([n[1] for n in children(one(out, 'structure'), 'layer')] == LAYERS,
           'Only the reviewed four-layer stack is supported')
    allowed = json.loads(allowed_path.read_text())
    refuse(isinstance(allowed, list) and all(isinstance(n, str) for n in allowed)
           and len(allowed) == len(set(allowed)) and allowed, 'Supply a nonempty exact net list')
    all_nets = nets(source)
    refuse(set(allowed) <= set(all_nets), 'Allowlist contains unknown nets')
    refuse(all(n in ALLOW for n in allowed), 'Allowlist exceeds reviewed ordinary digital scope')
    refuse({p for pins in padmap(source).values() for p in pins} <= placed_pins(source),
           'A network pad is absent from the physical library')
    held = [n for n in all_nets if n not in allowed]
    network = one(out, 'network')
    refuse(all(not isinstance(n, list) or n[0] in ['net', 'class'] for n in network),
           'Unknown network constraints need review')
    original_classes = list(children(network, 'class'))
    assigned = []
    for original in original_classes:
        network.remove(original)
        names = [n for n in original[2:] if isinstance(n, str)]
        assigned.extend(names)
        for selected in [True, False]:
            members = [n for n in names if (n in allowed) == selected]
            if not members:
                continue
            # Preserve every original rule, especially held-net 0.20/0.25 mm
            # clearances. Suppression must never flatten a stricter net class.
            body = copy.deepcopy([n for n in original[2:] if isinstance(n, list)])
            node = ['class', ('route_' if selected else 'hold_') + original[1]] + members + body
            circuits = children(node, 'circuit')
            if not circuits:
                node.append(['circuit'])
            circuit = one(node, 'circuit')
            for layer_rule in list(children(circuit, 'use_layer')):
                circuit.remove(layer_rule)
            circuit.append(['use_layer'] + (['F.Cu', 'B.Cu'] if selected else ['In1.Cu']))
            if selected:
                for via_rule in list(children(circuit, 'use_via')):
                    circuit.remove(via_rule)
                circuit.append(['use_via', VIA])
                for rule in children(node, 'rule'):
                    for width in children(rule, 'width'):
                        width[1] = '200'
            for shove in list(children(node, 'shove_fixed')):
                node.remove(shove)
            node.append(['shove_fixed', 'off'])
            network.append(node)
    refuse(set(assigned) == set(all_nets) and len(assigned) == len(set(assigned)),
           'Every net must belong to exactly one input class')
    structure = one(out, 'structure')
    refuse(not children(structure, 'autoroute_settings'), 'Existing router settings need review')
    refuse(VIA in one(structure, 'via')[1:], 'Required digital via is unavailable')
    via = next((n for n in children(one(out, 'library'), 'padstack') if n[1] == VIA), None)
    refuse(via is not None and [n[1] for n in children(via, 'shape')] ==
           [['circle', l, '600'] for l in LAYERS], 'Unexpected through-via copper geometry')
    for layer in children(structure, 'layer'):
        one(layer, 'type')[1] = 'signal' if layer[1] in ['F.Cu', 'B.Cu'] else 'power'
    for rule in list(children(structure, 'rule')):
        structure.remove(rule)
    structure.append(['rule', ['width', '200'], ['clearance', '150'],
                      ['clearance', '150', ['type', 'smd_smd']]])
    settings = ['autoroute_settings', ['fanout', 'off'], ['autoroute', 'on'],
                ['postroute', 'off'], ['vias', 'on']] + [
        ['layer_rule', l, ['active', 'on' if l in ['F.Cu', 'B.Cu'] else 'off']]
        for l in LAYERS]
    # 2.4.1 silently skips remaining input if settings follow a plane scope.
    last_layer = max(i for i, n in enumerate(structure) if isinstance(n, list) and n[0] == 'layer')
    structure.insert(last_layer + 1, settings)
    for w in one(out, 'wiring')[1:]:
        refuse(w[0] in ['wire', 'via'], 'Unsupported fixed-copper shape')
        for t in list(children(w, 'type')):
            w.remove(t)
        w.append(['type', 'protect'])
    for tag in ['placement', 'library']:
        refuse(one(source, tag) == one(out, tag), tag + ' changed')
    refuse(padmap(source) == padmap(out), 'Pin mapping changed')
    for tag in ['boundary', 'plane', 'keepout', 'via', 'via_keepout', 'place_keepout']:
        refuse(children(one(source, 'structure'), tag) == children(structure, tag), tag + ' changed')
    refuse(copper_signatures(source) == copper_signatures(out), 'Fixed-copper geometry changed')
    emitted = fmt(out) + '\n'
    refuse(parse(emitted) == out, 'DSN round-trip failed')
    project = board.with_suffix('.kicad_pro')
    refuse(project.is_file(), 'Matching source project settings are required')
    report = {
        'profile': 'fixed copper and full-network layer-intersection suppression',
        'source': str(dsn.resolve()), 'source_sha256': sha(raw),
        'source_board': str(board.resolve()), 'source_board_sha256': sha(board.read_bytes()),
        'source_project': str(project.resolve()), 'source_project_sha256': sha(project.read_bytes()),
        'output': str(dest.resolve()), 'output_sha256': sha(emitted.encode()),
        'selected_nets': allowed, 'held_nets': held,
        'source_net_count': len(all_nets), 'placed_components': len(placement_signature(source)),
        'physical_copper_pins': len(placed_pins(source)),
        'fixed_copper_items': sum(copper_signatures(source).values()),
        'keepout_definitions': count(source, 'keepout'),
        'all_pin_maps_preserved': True, 'all_geometry_preserved': True,
        'original_netclass_clearances_preserved': True,
        'input_classes': len(original_classes),
        'routing_classes': len(children(network, 'class')),
        'required_settings': {'copper_to_edge_clearance_um': 500, 'hole_clearance_um': 250,
                              'automatic_neckdown': False, 'strict_drc': True},
        'jar_sha256': '251101c3eeac22d7e7dfcf6796603279e5d1000283eb82d8f093780f7afc6aa9',
        'scope': 'Four-layer 0.20 mm digital routing with 0.6/0.3 mm through vias. Native DRC and visual/electrical checks remain separate.'}
    dest.write_text(emitted)
    manifest.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['placed_components', 'physical_copper_pins', 'fixed_copper_items', 'source_net_count']}))


def audit_fixed(ses, manifest, router_result, output):
    refuse(not output.exists(), 'Audit output must be new')
    m = json.loads(manifest.read_text())
    for pathkey, hashkey in [('output', 'output_sha256'), ('source', 'source_sha256'),
                             ('source_board', 'source_board_sha256'), ('source_project', 'source_project_sha256')]:
        refuse(sha(pathlib.Path(m[pathkey]).read_bytes()) == m[hashkey], pathkey + ' changed')
    src = parse(pathlib.Path(m['output']).read_text())
    result = parse(ses.read_text())
    refuse(result[0] == 'session', 'Not a SES')
    engine = json.loads(router_result.read_text())
    refuse(engine['fixture']['sha256'] == m['output_sha256'], 'Engine input hash mismatch')
    stats = engine['board_statistics']
    refuse(stats['components']['total_count'] == m['placed_components']
           and stats['pads']['total_count'] == m['physical_copper_pins']
           and stats['nets']['total_count'] == m['source_net_count'], 'Router lost components/pads/networks')
    refuse(stats['layers'] == {'total_count': 4, 'signal_count': 2}, 'Router stackup mismatch')
    settings = engine['settings_snapshot']
    for key, value in m['required_settings'].items():
        refuse(settings.get(key) == value, 'Engine setting mismatch: ' + key)
    refuse(settings['fanout']['enabled'] is False and settings['optimizer']['enabled'] is False,
           'Unreviewed fanout/optimizer enabled')
    refuse(placement_signature(src) == placement_signature(result, True), 'Router moved a footprint')
    fixed = copper_signatures(src)
    routed = copper_signatures(result, True)
    missing, new = fixed-routed, routed-fixed
    errors = []
    if missing:
        errors.append('Missing/modified fixed copper: ' + str(sum(missing.values())))
    for item in new:
        if item[1] not in m['selected_nets']:
            errors.append('Added copper on held net: ' + item[1])
        if item[0] == 'wire' and (item[2] not in ['F.Cu', 'B.Cu'] or item[3] != 2000):
            errors.append('Unexpected new track layer/width: ' + item[1])
        if item[0] == 'via' and item[2] != VIA:
            errors.append('Unexpected new via: ' + item[1])
    report = {'manifest_sha256': sha(manifest.read_bytes()), 'ses_sha256': sha(ses.read_bytes()),
              'router_result_sha256': sha(router_result.read_bytes()),
              'fixed_copper_items': sum(fixed.values()), 'missing_fixed': sum(missing.values()),
              'added_tracks': sum(v for k, v in new.items() if k[0] == 'wire'),
              'added_vias': sum(v for k, v in new.items() if k[0] == 'via'),
              'added_by_net': dict(collections.Counter(k[1] for k in new.elements())),
              'held_net_additions': sum(v for k, v in new.items() if k[1] not in m['selected_nets']),
              'all_networks_and_obstacles_loaded': True, 'placement_unchanged': True,
              'router_state': engine.get('final_state'),
              'errors': sorted(set(errors)), 'passed': not errors}
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'added_by_net'}))
    refuse(not errors, '; '.join(sorted(set(errors))))



def audit_assembly_vias(board, original_ids):
    """Reject new via annuli intersecting any SMD copper/paste land, even same-net."""
    import pcbnew as p
    def polygon(item, layer, clearance=0):
        poly = p.SHAPE_POLY_SET()
        item.TransformShapeToPolygon(poly, layer, clearance, p.FromMM(.001), p.ERROR_OUTSIDE)
        return poly
    def intersects(a, b):
        if not a.OutlineCount() or not b.OutlineCount() or not a.BBox().Intersects(b.BBox()):
            return False
        intersection = p.SHAPE_POLY_SET()
        intersection.BooleanIntersection(a, b)
        return intersection.Area() > 0
    lands = []
    expanded_paste = 0
    for footprint in board.GetFootprints():
        refuse(not any(g.GetLayer() in [p.F_Paste, p.B_Paste] for g in footprint.GraphicalItems()),
               'Standalone paste graphics need explicit assembly geometry review')
        for pad in footprint.Pads():
            if pad.GetAttribute() != p.PAD_ATTRIB_SMD:
                continue
            for copper, paste in [(p.F_Cu, p.F_Paste), (p.B_Cu, p.B_Paste)]:
                if not pad.IsOnLayer(copper):
                    continue
                expansion = 0
                if pad.IsOnLayer(paste):
                    margin = pad.GetSolderPasteMargin(copper)
                    expansion = max(0, margin.x, margin.y)
                    expanded_paste += int(expansion > 0)
                # Copper bounds negative/zero paste margins. For positive paste
                # margin use the conservative larger axis on the native polygon.
                lands.append((footprint, pad, copper, polygon(pad, copper, expansion)))
    vias = [t for t in board.GetTracks() if isinstance(t, p.PCB_VIA)
            and t.m_Uuid.AsString() not in original_ids]
    hits = []
    for via in vias:
        for footprint, pad, layer, shape in lands:
            if intersects(polygon(via, layer), shape):
                hits.append({'via_uuid': via.m_Uuid.AsString(), 'net': via.GetNetname(),
                             'reference': footprint.GetReference(), 'pad': pad.GetNumber(),
                             'layer': board.GetLayerName(layer),
                             'same_net': via.GetNetCode() == pad.GetNetCode()})
    return {'new_vias': len(vias), 'smd_lands_checked': len(lands),
            'positive_paste_expansions': expanded_paste, 'intersection_count': len(hits),
            'intersections': hits, 'passed': not hits,
            'method': 'Native copper/paste envelope polygons, 1 um conservative approximation; original source vias excluded by UUID.'}

def import_fixed(ses, manifest, audit_path, dest, report_path):
    """Native import into memory; transfer only audited additions to pristine base.

    Native DSN export rounds copper to 1 um, and SES can round footprint poses.
    Never replace the original source objects with those rounded import objects.
    """
    import pcbnew as p
    import shutil
    refuse(not dest.exists() and not report_path.exists(), 'Outputs must be new')
    m = json.loads(manifest.read_text())
    audit = json.loads(audit_path.read_text())
    refuse(audit['passed'] and audit['manifest_sha256'] == sha(manifest.read_bytes())
           and audit['ses_sha256'] == sha(ses.read_bytes()), 'Missing/stale passing audit')
    source = pathlib.Path(m['source_board'])
    project = pathlib.Path(m['source_project'])
    refuse(sha(source.read_bytes()) == m['source_board_sha256']
           and sha(project.read_bytes()) == m['source_project_sha256'], 'Source revision changed')
    base, imported = p.LoadBoard(str(source)), p.LoadBoard(str(source))
    io = p.PCB_IO_KICAD_SEXPR()
    def native_format(item):
        io.Format(item)
        return io.GetStringOutput(True)
    def snapshot(board):
        return {
            'footprints': {f.m_Uuid.AsString(): native_format(f) for f in board.GetFootprints()},
            'drawings': {d.m_Uuid.AsString(): native_format(d) for d in board.GetDrawings()},
            'copper': {t.m_Uuid.AsString(): native_format(t) for t in board.GetTracks()},
            'zones': {z.m_Uuid.AsString(): [n for n in parse(native_format(z)) if not isinstance(n, list)
                      or n[0] not in ['filled_polygon', 'fill_segments']] for z in board.Zones()}}
    def near(a, b):
        if type(a) != type(b) or a.GetNetname() != b.GetNetname():
            return False
        def close(u, v):
            return max(abs(u.x-v.x), abs(u.y-v.y)) <= 501
        if isinstance(a, p.PCB_VIA):
            return (a.TopLayer() == b.TopLayer() and a.BottomLayer() == b.BottomLayer()
                    and a.GetWidth(p.F_Cu) == b.GetWidth(p.F_Cu)
                    and close(a.GetPosition(), b.GetPosition()))
        return (a.GetLayer() == b.GetLayer() and a.GetWidth() == b.GetWidth()
                and ((close(a.GetStart(), b.GetStart()) and close(a.GetEnd(), b.GetEnd()))
                     or (close(a.GetStart(), b.GetEnd()) and close(a.GetEnd(), b.GetStart()))))
    before = snapshot(base)
    refuse(len(before['copper']) == m['fixed_copper_items'], 'Native/DSN fixed-item count mismatch')
    refuse(p.ImportSpecctraSES(imported, str(ses)), 'Native SES import failed')
    additions = list(imported.GetTracks())
    restored_drills = []
    for old in base.GetTracks():
        matches = [t for t in additions if near(old, t)]
        def exact_geometry(t):
            if isinstance(t, p.PCB_VIA):
                return ('via', t.GetNetname(), t.TopLayer(), t.BottomLayer(), t.GetWidth(p.F_Cu),
                        t.GetDrillValue(), t.GetPosition().x, t.GetPosition().y)
            return ('wire', t.GetNetname(), t.GetLayer(), t.GetWidth(),
                    tuple(sorted(((t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)))))
        # Source can already contain identical duplicate segments. Preserve their
        # multiplicity; only truly different near-matches are ambiguous.
        refuse(bool(matches) and len({exact_geometry(t) for t in matches}) == 1,
               'Fixed native geometry missing/ambiguous: ' + old.GetNetname())
        if isinstance(old, p.PCB_VIA) and old.GetDrillValue() != matches[0].GetDrillValue():
            # SES has no explicit drill field; native import can substitute a
            # netclass drill. SES identity was verified above. Keep the source.
            restored_drills.append({'uuid': old.m_Uuid.AsString(), 'net': old.GetNetname(),
                                    'source_drill_mm': p.ToMM(old.GetDrillValue()),
                                    'discarded_import_drill_mm': p.ToMM(matches[0].GetDrillValue())})
        additions.remove(matches[0])
    refuse(len(additions) == audit['added_tracks'] + audit['added_vias'], 'Added-item count mismatch')
    for item in additions:
        refuse(item.GetNetname() in m['selected_nets'], 'Added held-net native copper')
        if isinstance(item, p.PCB_VIA):
            refuse(item.TopLayer() == p.F_Cu and item.BottomLayer() == p.B_Cu
                   and item.GetWidth(p.F_Cu) == p.FromMM(.6) and item.GetDrillValue() == p.FromMM(.3),
                   'Unexpected native via')
            new = p.PCB_VIA(base)
            new.SetPosition(item.GetPosition())
            new.SetWidth(item.GetWidth(p.F_Cu))
            new.SetDrill(item.GetDrillValue())
            new.SetViaType(p.VIATYPE_THROUGH)
            new.SetLayerPair(p.F_Cu, p.B_Cu)
        else:
            refuse(item.GetLayer() in [p.F_Cu, p.B_Cu] and item.GetWidth() == p.FromMM(.2),
                   'Unexpected native track')
            new = p.PCB_TRACK(base)
            new.SetStart(item.GetStart())
            new.SetEnd(item.GetEnd())
            new.SetWidth(item.GetWidth())
            new.SetLayer(item.GetLayer())
        new.SetNet(base.FindNet(item.GetNetname()))
        base.Add(new)
    def verify(board):
        after = snapshot(board)
        for key in ['footprints', 'drawings', 'zones']:
            refuse(before[key] == after[key], 'Native ' + key + ' changed')
        refuse(all(after['copper'].get(k) == v for k, v in before['copper'].items()),
               'Original native copper changed')
    assembly = audit_assembly_vias(base, set(before['copper']))
    if not assembly['passed']:
        report_path.write_text(json.dumps({'status': 'rejected_before_save', 'assembly_via_check': assembly}, indent=2)+'\n')
        raise ValueError('New via intersects an SMD copper/paste land; candidate not saved')
    base.BuildConnectivity()
    p.ZONE_FILLER(base).Fill(base.Zones())
    verify(base)
    p.SaveBoard(str(dest), base)
    shutil.copy2(project, dest.with_suffix('.kicad_pro'))
    verify(p.LoadBoard(str(dest)))
    refuse(sha(source.read_bytes()) == m['source_board_sha256']
           and sha(project.read_bytes()) == m['source_project_sha256'], 'Source was changed')
    report = {'source_sha256': m['source_board_sha256'], 'candidate_sha256': sha(dest.read_bytes()),
              'original_copper_items_preserved_exactly': len(before['copper']),
              'added_tracks': audit['added_tracks'], 'added_vias': audit['added_vias'],
              'footprints_drawings_zone_definitions_unchanged': True,
              'original_copper_uuid_and_serialization_unchanged': True,
              'held_net_additions': 0, 'zones_refilled': True, 'source_unchanged': True,
              'native_import_drill_substitutions_discarded': restored_drills,
              'assembly_via_check': assembly,
              'native_drc': 'REQUIRED: run full native DRC and compare to source before adoption'}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


def run_local(dsn, manifest, ses, result, java, jar, max_passes=2, timeout_seconds=90):
    """Run the existing pinned engine locally, bounded and without services/analytics."""
    import subprocess
    import time
    import os
    import signal
    m = json.loads(manifest.read_text())
    refuse(1 <= max_passes <= 6 and 10 <= timeout_seconds <= 180, 'Use 1-6 passes and 10-180 seconds')
    refuse(sha(dsn.read_bytes()) == m['output_sha256'], 'Prepared DSN hash mismatch')
    refuse(sha(jar.read_bytes()) == m['jar_sha256'], 'Unreviewed Freerouting JAR')
    refuse(java.is_file(), 'Existing Java executable is required')
    log = result.with_suffix('.log')
    command_file = result.with_suffix('.command.json')
    run_report = result.with_suffix('.run.json')
    user_dir = result.parent / (result.stem + '-user')
    for path in [ses, result, log, command_file, run_report, user_dir]:
        refuse(not path.exists(), 'Output already exists: ' + str(path))
    job_time = f'{timeout_seconds//3600:02}:{timeout_seconds//60%60:02}:{timeout_seconds%60:02}'
    command = [str(java.resolve()), '-Xmx2g', '-jar', str(jar.resolve()),
               '-de', str(dsn.resolve()), '-do', str(ses.resolve()), '-mp', str(max_passes),
               '-mt', '1', '-da', '--gui.enabled=false', '--api_server.enabled=false',
               '--mcp_server.enabled=false', '--profile.allow_telemetry=false',
               '--router.fanout.enabled=false', '--router.optimizer.enabled=false',
               '--router.copper_to_edge_clearance_um=500', '--router.hole_clearance_um=250',
               '--router.automatic_neckdown=false', '--router.strict_drc=true',
               '--router.job_timeout=' + job_time, '--router.result_json=' + str(result.resolve()),
               '--user_data_path=' + str(user_dir.resolve()), '--logging.file.enabled=false']
    command_file.write_text(json.dumps(command, indent=2) + '\n')
    started = time.monotonic()
    timeout = False
    with log.open('w') as stream:
        proc = subprocess.Popen(command, cwd=result.parent.resolve(), stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = proc.wait(timeout=timeout_seconds + 15)
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                code = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                code = proc.wait()
    report = {'elapsed_seconds': round(time.monotonic()-started, 2), 'exit_code': code,
              'external_timeout': timeout, 'ses_exists': ses.is_file(), 'result_exists': result.is_file(),
              'not_a_design_verdict': 'SES audit and native DRC are required after every run'}
    run_report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    refuse(ses.is_file() and result.is_file(), 'Router output incomplete; inspect the saved log before retrying')

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare'); p.add_argument('dsn',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);p.add_argument('manifest',type=pathlib.Path)
    p=sub.add_parser('audit-ses');p.add_argument('ses',type=pathlib.Path);p.add_argument('manifest',type=pathlib.Path);p.add_argument('output',type=pathlib.Path)
    p=sub.add_parser('prepare-fixed')
    for n in ['dsn','board','allowed_nets','output','manifest']:p.add_argument(n,type=pathlib.Path)
    p=sub.add_parser('audit-fixed-ses')
    for n in ['ses','manifest','router_result','output']:p.add_argument(n,type=pathlib.Path)
    p=sub.add_parser('import-fixed')
    for n in ['ses','manifest','audit','output','report']:p.add_argument(n,type=pathlib.Path)
    p=sub.add_parser('run-local')
    for n in ['dsn','manifest','ses','result','java','jar']:p.add_argument(n,type=pathlib.Path)
    p.add_argument('--max-passes',type=int,default=2)
    p.add_argument('--timeout-seconds',type=int,default=90)
    a=ap.parse_args()
    if a.command=='prepare':prepare(a.dsn,a.output,a.manifest)
    elif a.command=='audit-ses':audit(a.ses,a.manifest,a.output)
    elif a.command=='prepare-fixed':prepare_fixed(a.dsn,a.board,a.allowed_nets,a.output,a.manifest)
    elif a.command=='audit-fixed-ses':audit_fixed(a.ses,a.manifest,a.router_result,a.output)
    elif a.command=='import-fixed':import_fixed(a.ses,a.manifest,a.audit,a.output,a.report)
    elif a.command=='run-local':run_local(a.dsn,a.manifest,a.ses,a.result,a.java,a.jar,a.max_passes,a.timeout_seconds)
if __name__=='__main__':main()
