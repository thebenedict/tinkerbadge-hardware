#!/usr/bin/env python3
"""Write Tinkerbadge.pretty/Expansion_Header_2x05_P2.54mm.kicad_mod.

Unpopulated 2 x 5, 2.54 mm expansion header J503 (docs/design/expansion_header.md).
Hole pattern, drill and pad size follow KiCad's
Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical, re-centred on the
middle of the header and rotated a quarter turn (not mirrored) so the rows run
along X: odd pins are the row nearer the top board edge and pin 1 is at the
RIGHT as seen from the front. A standard header or socket fitted on the front
therefore keeps its own pin numbers. Seen from the rear, pin 1 is at the left.

Signal names are printed beside each pin. The rear names all ten pins; the
front names the top row only, because the bottom row sits against the display
glass. Text is 1.0 mm high with 0.15 mm strokes, the project's JLCPCB minimum.
"""
import pathlib
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'Tinkerbadge.pretty' / 'Expansion_Header_2x05_P2.54mm.kicad_mod'

PITCH = 2.54
DRILL = 1.0
PAD = 1.7
TOP = {1: 'GND', 3: '3V3', 5: 'SDA', 7: 'SCL', 9: 'IO4'}
BOTTOM = {2: 'TX', 4: 'RX', 6: 'IO42', 8: 'IO47', 10: 'GND'}
# KiCad bounding-box width of each label at 1.0 mm / 0.15 mm, measured with pcbnew
WIDTH = {'GND': 3.30, '3V3': 3.01, 'SDA': 3.06, 'SCL': 3.01, 'IO4': 2.73,
         'TX': 1.96, 'RX': 2.20, 'IO42': 3.68, 'IO47': 3.68}
GAP = 0.30          # pad edge to the near end of a label
NS = uuid.UUID('6f0c2f0a-3d0b-4a53-9c33-2b8f5a0c1e77')
_n = [0]


def uid():
    _n[0] += 1
    return str(uuid.uuid5(NS, f'expansion-header-{_n[0]}'))


def pad_xy(n):
    col = (n - 1) // 2
    return (2 - col) * PITCH, (-PITCH / 2 if n % 2 else PITCH / 2)


def text(s, x, y, layer, angle=0):
    mirror = ' (justify mirror)' if layer.startswith('B.') else ''
    return (f'\t(fp_text user "{s}" (at {x:.3f} {y:.3f} {angle}) (layer "{layer}") (uuid "{uid()}") '
            f'(effects (font (size 1.0 1.0) (thickness 0.15)){mirror}))')


def line(x0, y0, x1, y1, layer, w):
    return (f'\t(fp_line (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f}) '
            f'(stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{uid()}"))')


def rect(x0, y0, x1, y1, layer, w):
    return (f'\t(fp_rect (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f}) '
            f'(stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{uid()}"))')


def triangle(layer):
    # pin-1 marker beside pin 1 (right of it from the front), pointing at it
    x, y = pad_xy(1)
    tip = x + PAD / 2 + 0.35
    pts = [(tip + 0.8, y - 0.5), (tip + 0.8, y + 0.5), (tip, y)]
    xy = ' '.join(f'(xy {px:.3f} {py:.3f})' for px, py in pts)
    return (f'\t(fp_poly (pts {xy}) (stroke (width 0.15) (type solid)) (fill yes) '
            f'(layer "{layer}") (uuid "{uid()}"))')


def labels(names, layer, above):
    out = []
    for n, s in names.items():
        x, y = pad_xy(n)
        near = PAD / 2 + GAP
        centre = y - near - WIDTH[s] / 2 if above else y + near + WIDTH[s] / 2
        out.append(text(s, x, centre, layer, 90))
    return out


body_x, body_y = 5 * PITCH / 2, PITCH            # fitted-header body half size: 6.35 x 2.54
o = ['(footprint "Expansion_Header_2x05_P2.54mm"',
     '\t(version 20241229)',
     '\t(generator "tinkerbadge_expansion_header")',
     '\t(layer "F.Cu")',
     '\t(descr "Unpopulated 2x5 2.54 mm expansion header, 1.0 mm drill, standard header numbering for a part fitted on the front. '
     'Front view, left to right: top row 9 IO4, 7 SCL, 5 SDA, 3 3V3, 1 GND; bottom row 10 GND, 8 IO47, 6 IO42, 4 RX, 2 TX. '
     '3.3 V signals only. See docs/design/expansion_header.md.")',
     '\t(tags "expansion header 2x05 2.54mm unpopulated")',
     f'\t(property "Reference" "REF**" (at -8.2 3.6 0) (layer "F.Fab") (uuid "{uid()}") (effects (font (size 0.8 0.8) (thickness 0.12))))',
     f'\t(property "Value" "Expansion_Header_2x05_P2.54mm" (at 0 4.4 0) (layer "F.Fab") (uuid "{uid()}") (effects (font (size 0.8 0.8) (thickness 0.12))))',
     '\t(attr through_hole exclude_from_pos_files exclude_from_bom dnp)']
for n in range(1, 11):
    x, y = pad_xy(n)
    shape = 'rect' if n == 1 else 'circle'
    o.append(f'\t(pad "{n}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {PAD} {PAD}) (drill {DRILL}) '
             f'(layers "*.Cu" "*.Mask") (uuid "{uid()}"))')
# fitted-header body on the fabrication layer, pin-1 corner chamfered
c = 1.0
for a, b in [((-body_x, -body_y), (body_x - c, -body_y)), ((body_x - c, -body_y), (body_x, -body_y + c)),
             ((body_x, -body_y + c), (body_x, body_y)), ((body_x, body_y), (-body_x, body_y)),
             ((-body_x, body_y), (-body_x, -body_y))]:
    o.append(line(*a, *b, 'F.Fab', 0.1))
# room for a header fitted on either side
for layer in ('F.CrtYd', 'B.CrtYd'):
    o.append(rect(-body_x - 0.25, -body_y - 0.25, body_x + 0.25, body_y + 0.25, layer, 0.05))
# front: top row and pin 1
o += labels(TOP, 'F.SilkS', above=True)
o.append(triangle('F.SilkS'))
# rear: both rows, pin 1 and the level warning
o += labels(TOP, 'B.SilkS', above=True)
o += labels(BOTTOM, 'B.SilkS', above=False)
o.append(triangle('B.SilkS'))
o.append(text('EXP 3V3 ONLY', -14.3, 0.0, 'B.SilkS'))
o.append(')')
OUT.write_text('\n'.join(o) + '\n')
print('wrote', OUT.relative_to(ROOT))
