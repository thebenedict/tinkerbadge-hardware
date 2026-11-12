#!/usr/bin/env python3
"""Generate the project-local footprints added by the 2026-11-10 design review.

Dock pads, the front-mounted SAO socket and the rear NFC coil are plain
geometry, so they are generated rather than hand-drawn. Re-run to regenerate.
"""
import pathlib
import uuid

OUT = pathlib.Path(__file__).resolve().parents[1] / 'Tinkerbadge.pretty'


def u():
    return str(uuid.uuid4())


def header(name, descr, attr, side='F'):
    return f'''(footprint "{name}"
\t(version 20241229)
\t(generator "tinkerbadge_review")
\t(layer "{side}.Cu")
\t(descr "{descr}")
\t(property "Reference" "REF**" (at 0 -4.5 0) (layer "{side}.SilkS") (uuid "{u()}") (effects (font (size 0.8 0.8) (thickness 0.12)){' (justify mirror)' if side == 'B' else ''}))
\t(property "Value" "{name}" (at 0 4.5 0) (layer "{side}.Fab") (uuid "{u()}") (effects (font (size 0.8 0.8) (thickness 0.12)){' (justify mirror)' if side == 'B' else ''}))
\t(attr {attr})
'''


def rect(layer, x0, y0, x1, y1, w=0.05):
    return f'\t(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{u()}"))\n'


def text(layer, s, x, y, size=0.8):
    mirror = ' (justify mirror)' if layer.startswith('B.') else ''
    return f'\t(fp_text user "{s}" (at {x} {y} 0) (layer "{layer}") (uuid "{u()}") (effects (font (size {max(size, 1.0)} {max(size, 1.0)}) (thickness 0.15)){mirror}))\n'


def dock():
    s = header('Dock_Pads_2x_4x6mm', 'Two bare ENIG landing pads for dock pogo pins, 8 mm pitch. Pad 1 = +5 V, pad 2 = GND.', 'smd exclude_from_pos_files exclude_from_bom', 'B')
    for n, x in (('1', -4), ('2', 4)):
        s += f'\t(pad "{n}" smd roundrect (at {x} 0) (size 4 6) (layers "B.Cu" "B.Mask") (roundrect_rratio 0.2) (uuid "{u()}"))\n'
    s += rect('B.CrtYd', -6.5, -3.5, 6.5, 3.5)
    s += text('B.SilkS', '+5V', -4, -4) + text('B.SilkS', 'GND', 4, -4)
    return s + ')\n'


def model(name):
    return (f'\t(model "${{KIPRJMOD}}/models/{name}"\n\t\t(offset (xyz 0 0 0))\n\t\t(scale (xyz 1 1 1))\n'
            f'\t\t(rotate (xyz 0 0 0))\n\t)\n')


def vrml(path, boxes, note):
    """Write an envelope model. boxes: (cx, cy, cz, sx, sy, sz, (r, g, b)) in mm, KiCad footprint axes (y down)."""
    k = 1 / 2.54
    out = ['#VRML V2.0 utf8', f'# {note}']
    for cx, cy, cz, sx, sy, sz, col in boxes:
        hx, hy, hz = sx / 2 * k, sy / 2 * k, sz / 2 * k
        pts = ', '.join(f'{x * hx:.6f} {y * hy:.6f} {z * hz:.6f}' for z in (-1, 1) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        out.append(f'Transform {{ translation {cx * k:.6f} {-cy * k:.6f} {cz * k:.6f} children [ Shape {{ appearance Appearance {{ material Material {{ '
                   f'diffuseColor {col[0]} {col[1]} {col[2]} transparency 0 }} }} geometry IndexedFaceSet {{ coord Coordinate {{ point [ {pts} ] }} '
                   f'coordIndex [ 0,3,2,1,-1, 4,5,6,7,-1, 0,1,5,4,-1, 1,2,6,5,-1, 2,3,7,6,-1, 3,0,4,7,-1 ] solid TRUE }} }} ] }}')
    pathlib.Path(path).write_text('\n'.join(out) + '\n')


def line(layer, x0, y0, x1, y1, w=0.15):
    return f'\t(fp_line (start {x0} {y0}) (end {x1} {y1}) (stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{u()}"))\n'


def poly(layer, pts, w=0.15):
    return ''.join(line(layer, *a, *b, w) for a, b in zip(pts, pts[1:] + pts[:1]))


def sao():
    """Sullins SFH11-NBPC-D03-ST-BK, drawing 11160 rev J: body 12.70 x 6.00 mm, 8.50 mm tall,
    with a 3.70 x 1.00 mm polarising key centred on one long side. The SAO v2 component list
    says the key aligns with the top row (pins 1/3/5), so the key is drawn toward -y."""
    s = header('SAO_Socket_2x03_Front', 'SAO host socket Sullins SFH11-NBPC-D03-ST-BK, 2x3 2.54 mm keyed female, 12.7 x 6.0 mm body plus 3.7 x 1.0 mm key on the top-row side, 8.5 mm tall. Viewed from the badge front: top row 3V3 SDA GPIO1, bottom row GND SCL GPIO2.', 'through_hole')
    pos = {'1': (-2.54, -1.27), '3': (0, -1.27), '5': (2.54, -1.27), '2': (-2.54, 1.27), '4': (0, 1.27), '6': (2.54, 1.27)}
    for n, (x, y) in pos.items():
        shape = 'rect' if n == '1' else 'circle'
        s += f'\t(pad "{n}" thru_hole {shape} (at {x} {y}) (size 1.6 1.6) (drill 1.02) (layers "*.Cu" "*.Mask") (uuid "{u()}"))\n'
    body = [(-6.35, -3.0), (-1.85, -3.0), (-1.85, -4.0), (1.85, -4.0), (1.85, -3.0), (6.35, -3.0), (6.35, 3.0), (-6.35, 3.0)]
    s += poly('F.Fab', body, 0.1)
    s += poly('F.SilkS', [(x + (0.12 if x > 0 else -0.12), y + (0.12 if y > 0 else -0.12)) for x, y in body], 0.15)
    s += rect('F.CrtYd', -6.6, -4.25, 6.6, 3.25)
    # labels sit beside the housing, below the neighbouring role LED: 3V3 is the upper pin of the
    # left-hand column (pin 1), GND the lower (pin 2)
    s += text('F.SilkS', '3V3', -8.45, 0.1, 1.0) + text('F.SilkS', 'GND', -8.45, 1.65, 1.0) + text('F.SilkS', 'SAO', 8.75, 1.9, 1.0)
    s += model('SAO_SFH11_2x03_envelope.wrl')
    vrml(OUT.parent / 'models/SAO_SFH11_2x03_envelope.wrl',
         [(0, 0, 4.25, 12.7, 6.0, 8.5, (0.12, 0.12, 0.12)), (0, -3.5, 4.25, 3.7, 1.0, 8.5, (0.12, 0.12, 0.12))],
         'Datasheet-derived envelope (Sullins drawing 11160 rev J), not vendor CAD.')
    return s + ')\n'


def fh34():
    """Hirose FH34SRJ-24S-0.5SH(50), catalogue dated Nov.1.2018 p.3-4: 24 signal lands 0.3 x 0.8 mm
    at 0.5 mm pitch over B = 11.5 mm; two metal-fitting lands 0.4 x 0.8 mm, E = 13.1 inner,
    F = 13.9 outer; 3.3 mm from the top of the signal lands to the bottom of the fitting lands.
    Body A = 14.0 x 3.8 mm overall, 1.0 mm high. FPC enters from the fitting-land (+y) side.

    Pads are numbered in PANEL order, not Hirose contact order: the panel flex folds under the
    glass, so panel pin 1 lands on Hirose contact 24. Pad "n" here is Hirose contact 25 - n."""
    s = header('Hirose_FH34SRJ-24S-0.5SH_PanelOrder', 'Hirose FH34SRJ-24S-0.5SH(50), 0.5 mm pitch, 1.0 mm high, back-flip, top and bottom contact. Pads numbered in display-panel order for the folded flex (pad n = Hirose contact 25-n). FPC enters from +y.', 'smd')
    for n in range(1, 25):
        x = -5.75 + 0.5 * (n - 1)
        s += (f'\t(pad "{n}" smd rect (at {x:.2f} -1.25) (size 0.3 0.8) (layers "F.Cu" "F.Paste" "F.Mask") '
              f'(solder_paste_margin -0.025) (uuid "{u()}"))\n')
    for x in (-6.75, 6.75):
        s += f'\t(pad "MP" smd rect (at {x} 1.25) (size 0.4 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{u()}"))\n'
    s += rect('F.Fab', -7.0, -2.04, 7.0, 1.8, 0.1)
    s += rect('F.CrtYd', -7.25, -2.3, 7.25, 2.05)
    # silkscreen: ends and front lip only, clear of the lands
    s += line('F.SilkS', -7.15, -2.0, -7.15, 0.55) + line('F.SilkS', 7.15, -2.0, 7.15, 0.55)
    s += line('F.SilkS', -6.25, 1.95, 6.25, 1.95)
    s += line('F.SilkS', -7.15, -2.0, -6.2, -2.0) + line('F.SilkS', 6.2, -2.0, 7.15, -2.0)
    s += f'\t(fp_circle (center -6.6 -2.6) (end -6.45 -2.6) (stroke (width 0.15) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{u()}"))\n'
    s += model('Hirose_FH34SRJ-24S_envelope.wrl')
    vrml(OUT.parent / 'models/Hirose_FH34SRJ-24S_envelope.wrl',
         [(0, -0.12, 0.5, 14.0, 3.84, 1.0, (0.85, 0.82, 0.74))],
         'Datasheet-derived envelope (Hirose FH34SRJ catalogue, Nov 2018), not vendor CAD.')
    return s + ')\n'


def coil(width=18.0, height=13.0, turns=10, w=0.2, gap=0.2):
    """Rectangular spiral drawn directly on B.Cu in front-view coordinates."""
    name = 'NFC_Coil_Rear_18x13'
    s = header(name, f'13.56 MHz NFC loop, {turns} turns, {w} mm track / {gap} mm gap, {width} x {height} mm outer. Estimated 1.7 uH (modified Wheeler); tune on the assembled badge.', 'smd exclude_from_pos_files exclude_from_bom', 'B')
    s += '\t(net_tie_pad_groups "1, 2")\n'
    pitch = w + gap
    x0, y0, x1, y1 = -width / 2 + w / 2, -height / 2 + w / 2, width / 2 - w / 2, height / 2 - w / 2
    pts = [(x0, y0)]
    for i in range(turns):
        pts += [(x1, y0), (x1, y1), (x0, y1), (x0, y0 + pitch)]
        x0 += pitch; y0 += pitch; x1 -= pitch; y1 -= pitch
        pts.append((x0, y0)) if False else None
        pts[-1] = (pts[-1][0], y0)
        pts.append((x0 if i < turns - 1 else pts[-1][0], y0)) if i < turns - 1 else None
    pts = [p for p in pts if p is not None]
    clean = [pts[0]]
    for q in pts[1:]:
        if q != clean[-1]:
            clean.append(q)
    # Lead-out above the outer corner and lead-in inside the clear centre so
    # that neither terminal pad sits against a neighbouring turn.
    clean.insert(0, (clean[0][0] - 1.1, clean[0][1]))
    ex, ey = clean[-1]
    clean[-1] = (ex, ey + 0.8)
    clean.append((ex + 1.1, ey + 0.8))
    for a, b in zip(clean, clean[1:]):
        s += f'\t(fp_line (start {a[0]:.3f} {a[1]:.3f}) (end {b[0]:.3f} {b[1]:.3f}) (stroke (width {w}) (type solid)) (layer "B.Cu") (uuid "{u()}"))\n'
    # pad 1 is the inner end and pad 2 the outer end: with the tag's LA pin facing the coil and
    # LB wrapping around the outside, the feed needs no crossing other than the inner lead-out
    s += f'\t(pad "1" smd circle (at {clean[-1][0]:.3f} {clean[-1][1]:.3f}) (size 0.6 0.6) (layers "B.Cu") (uuid "{u()}"))\n'
    s += f'\t(pad "2" smd circle (at {clean[0][0]:.3f} {clean[0][1]:.3f}) (size 0.6 0.6) (layers "B.Cu") (uuid "{u()}"))\n'
    s += rect('B.CrtYd', -width / 2 - 0.25, -height / 2 - 0.25, width / 2 + 0.25, height / 2 + 0.25)
    s += text('B.SilkS', 'NFC', 0, 1.2, 1.2)
    return name, s + ')\n', clean


if __name__ == '__main__':
    (OUT / 'Dock_Pads_2x_4x6mm.kicad_mod').write_text(dock())
    (OUT / 'SAO_Socket_2x03_Front.kicad_mod').write_text(sao())
    (OUT / 'Hirose_FH34SRJ-24S-0.5SH_PanelOrder.kicad_mod').write_text(fh34())
    name, body, pts = coil()
    (OUT / f'{name}.kicad_mod').write_text(body)
    length = sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(pts, pts[1:]))
    print(f'coil: {len(pts) - 1} segments, {length:.0f} mm, start {pts[0]}, end {pts[-1]}')
