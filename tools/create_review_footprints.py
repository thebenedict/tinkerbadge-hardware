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
    return f'\t(fp_text user "{s}" (at {x} {y} 0) (layer "{layer}") (uuid "{u()}") (effects (font (size {size} {size}) (thickness {size * 0.15:.2f})){mirror}))\n'


def dock():
    s = header('Dock_Pads_2x_4x6mm', 'Two bare ENIG landing pads for dock pogo pins, 8 mm pitch. Pad 1 = +5 V, pad 2 = GND.', 'smd exclude_from_pos_files exclude_from_bom', 'B')
    for n, x in (('1', -4), ('2', 4)):
        s += f'\t(pad "{n}" smd roundrect (at {x} 0) (size 4 6) (layers "B.Cu" "B.Mask") (roundrect_rratio 0.2) (uuid "{u()}"))\n'
    s += rect('B.CrtYd', -6.5, -3.5, 6.5, 3.5)
    s += text('B.SilkS', '+5V', -4, -4) + text('B.SilkS', 'GND', 4, -4)
    return s + ')\n'


def sao():
    s = header('SAO_Socket_2x03_Front', 'SAO v1.69bis host socket, 2x3 2.54 mm female, viewed from the badge front: top row 3V3 SDA GPIO1, bottom row GND SCL GPIO2.', 'through_hole')
    pos = {'1': (-2.54, -1.27), '3': (0, -1.27), '5': (2.54, -1.27), '2': (-2.54, 1.27), '4': (0, 1.27), '6': (2.54, 1.27)}
    for n, (x, y) in pos.items():
        shape = 'rect' if n == '1' else 'circle'
        s += f'\t(pad "{n}" thru_hole {shape} (at {x} {y}) (size 1.6 1.6) (drill 1.0) (layers "*.Cu" "*.Mask") (uuid "{u()}"))\n'
    s += rect('F.Fab', -3.94, -2.67, 3.94, 2.67, 0.1) + rect('F.CrtYd', -4.3, -3.0, 4.3, 3.0)
    s += rect('F.SilkS', -4.05, -2.8, 4.05, 2.8, 0.12)
    s += f'\t(fp_line (start -1 2.8) (end 1 2.8) (stroke (width 0.3) (type solid)) (layer "F.SilkS") (uuid "{u()}"))\n'
    s += text('F.SilkS', 'SAO', 0, -3.6, 0.8) + text('F.SilkS', '3V3', -5.9, -1.27, 0.8) + text('F.SilkS', 'GND', -5.9, 1.27, 0.8)
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
    s += f'\t(pad "1" smd circle (at {clean[0][0]:.3f} {clean[0][1]:.3f}) (size 0.6 0.6) (layers "B.Cu") (uuid "{u()}"))\n'
    s += f'\t(pad "2" smd circle (at {clean[-1][0]:.3f} {clean[-1][1]:.3f}) (size 0.6 0.6) (layers "B.Cu") (uuid "{u()}"))\n'
    s += rect('B.CrtYd', -width / 2 - 0.25, -height / 2 - 0.25, width / 2 + 0.25, height / 2 + 0.25)
    s += text('B.SilkS', 'NFC', 0, 1.2, 1.2)
    return name, s + ')\n', clean


if __name__ == '__main__':
    (OUT / 'Dock_Pads_2x_4x6mm.kicad_mod').write_text(dock())
    (OUT / 'SAO_Socket_2x03_Front.kicad_mod').write_text(sao())
    name, body, pts = coil()
    (OUT / f'{name}.kicad_mod').write_text(body)
    length = sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(pts, pts[1:]))
    print(f'coil: {len(pts) - 1} segments, {length:.0f} mm, start {pts[0]}, end {pts[-1]}')
