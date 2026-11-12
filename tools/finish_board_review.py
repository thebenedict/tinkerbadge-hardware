#!/usr/bin/env python3
"""Silkscreen, references and annotation pass. KiCad Python. Idempotent.

Usage: finish_board_review.py BOARD [NETLIST]

- copies Description/Datasheet fields from the netlist so schematic parity is clean;
- rewrites the board-level labels (buttons, ports, probe pads, revision);
- puts reference designators on silkscreen for ICs, connectors, switches, inductors,
  transistors, diodes and LEDs wherever a 1.0 mm label fits without touching pads,
  holes, other labels or the board edge; everything else keeps its reference on the
  fabrication layer for the assembly drawings;
- keeps all silkscreen at JLCPCB's legend minimum (1.0 mm high, 0.15 mm stroke).
"""
import pathlib
import sys

import pcbnew

MM = pcbnew.FromMM
REV = 'rev 0.3  2026-11-11'

LABELS = [
    # text, x, y, layer, size, rotation
    ('RST', 106.6, 132.4, 'F', 1.0, 0),
    ('A', 105.6, 142.2, 'F', 1.2, 0),
    ('B/BOOT', 108.4, 152.2, 'F', 1.0, 0),
    ('USB', 201.0, 119.6, 'F', 1.0, 0),
    ('QWIIC', 203.2, 154.2, 'F', 1.0, 0),
    ('EPD', 199.3, 146.2, 'F', 1.0, 0),
    ('TINKER BADGE', 126.0, 110.6, 'B', 2.0, 0),
    # rear text sits where no via or hole breaks it: the organisation under the title, revision
    # and licence on the bottom strip below the cell
    ('AI Tinkerers Seattle', 126.1, 113.2, 'B', 1.0, 0),
    (REV, 146.0, 178.0, 'B', 1.0, 0),
    ('CERN-OHL-P-2.0', 163.5, 178.0, 'B', 1.0, 0),
    ('EN', 174.0, 118.2, 'B', 1.0, 0), ('BOOT', 177.0, 113.8, 'B', 1.0, 0), ('3V3', 180.0, 118.2, 'B', 1.0, 0),
    ('GND', 183.0, 113.8, 'B', 1.0, 0), ('TX', 186.0, 118.2, 'B', 1.0, 0), ('RX', 189.0, 113.8, 'B', 1.0, 0),
    ('VSYS', 192.0, 118.2, 'B', 1.0, 0), ('EPD', 195.0, 113.8, 'B', 1.0, 0), ('SDA', 198.0, 118.2, 'B', 1.0, 0),
    ('SCL', 201.0, 113.8, 'B', 1.0, 0),
    ('BAT +', 174.6, 143.6, 'B', 1.0, 0), ('-', 178.4, 143.6, 'B', 1.0, 0),
    ('1S LiPo 4.2V  CHECK POLARITY', 180.6, 137.0, 'B', 1.0, 90),
    ('DOCK', 124.0, 170.4, 'B', 1.0, 0),
    ('TAP PHONE', 191.0, 163.6, 'B', 1.0, 0),
]
NOTES = {
    'TINKER BADGE 110 x 80': 'TINKER BADGE 110 x 80 - REV 0.3 2026-11-11 - PROTOTYPE, VISUAL REVIEW REQUIRED',
    'EXPERIMENTAL 110 x 80': 'TINKER BADGE 110 x 80 - REV 0.3 2026-11-11 - PROTOTYPE, VISUAL REVIEW REQUIRED',
    'NFC 18 x 13 RESERVE': 'NFC COIL - REAR',
}
SILK_REF_PREFIXES = ('U', 'J', 'SW', 'L', 'Q', 'RT', 'D')
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)


def netlist_fields(path):
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from schlib import parse, kids, kid
    out = {}
    for c in kids(kid(parse(open(path).read()), 'components'), 'comp'):
        d = {'Description': kid(c, 'description')[1] if kid(c, 'description') and len(kid(c, 'description')) > 1 else ''}
        for fld in kids(kid(c, 'fields') or ['fields'], 'field'):
            if kid(fld, 'name')[1] == 'Datasheet' and len(fld) > 2 and isinstance(fld[2], str):
                d['Datasheet'] = fld[2]
        out[kid(c, 'ref')[1]] = d
    return out


def style(t, size=1.0):
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(max(0.15, size * 0.15)))


def place_references(b):
    """Greedy label placement around each selected footprint."""
    outline = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outline, True)
    outline.Deflate(MM(0.6), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.05))
    blocked = {False: [], True: []}          # keyed by "is rear"
    for f in b.GetFootprints():
        for p in f.Pads():
            r = p.GetBoundingBox()
            r.Inflate(MM(0.25))
            if p.GetDrillSize().x > 0:
                blocked[False].append(r)
                blocked[True].append(r)
            else:
                blocked[p.IsOnLayer(pcbnew.B_Cu)].append(r)
        for g in f.GraphicalItems():
            if g.GetLayer() in SILK:
                r = g.GetBoundingBox()
                r.Inflate(MM(0.15))
                blocked[g.GetLayer() == pcbnew.B_SilkS].append(r)
    for d in b.GetDrawings():
        if d.GetLayer() in SILK:
            r = d.GetBoundingBox()
            r.Inflate(MM(0.2))
            blocked[d.GetLayer() == pcbnew.B_SilkS].append(r)
    placed = skipped = 0
    todo = [f for f in b.GetFootprints() if f.GetReference().startswith(SILK_REF_PREFIXES)
            and not f.GetReference().startswith(('FID', 'MECH', 'RES', 'H'))]
    todo.sort(key=lambda f: -f.GetBoundingBox(False).GetArea())     # big parts choose first
    for f in todo:
        rear = f.IsFlipped()
        if rear:
            continue                         # rear features carry functional labels instead
        ref = f.Reference()
        bb = f.GetBoundingBox(False)
        cx, cy = bb.GetCenter().x, bb.GetCenter().y
        ref.SetLayer(pcbnew.F_SilkS)
        ref.SetVisible(True)
        ref.SetTextAngleDegrees(0)
        ref.SetKeepUpright(True)
        style(ref, 1.0)
        w = ref.GetBoundingBox().GetWidth()
        h = ref.GetBoundingBox().GetHeight()
        gap = MM(0.35)
        cands = [(cx, bb.GetTop() - gap - h // 2), (cx, bb.GetBottom() + gap + h // 2),
                 (bb.GetLeft() - gap - w // 2, cy), (bb.GetRight() + gap + w // 2, cy),
                 (bb.GetLeft() + w // 2, bb.GetTop() - gap - h // 2), (bb.GetRight() - w // 2, bb.GetTop() - gap - h // 2),
                 (bb.GetLeft() + w // 2, bb.GetBottom() + gap + h // 2), (bb.GetRight() - w // 2, bb.GetBottom() + gap + h // 2)]
        done = False
        for x, y in cands:
            ref.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
            r = ref.GetBoundingBox()
            corners = [(r.GetLeft(), r.GetTop()), (r.GetRight(), r.GetTop()), (r.GetLeft(), r.GetBottom()), (r.GetRight(), r.GetBottom())]
            if not all(outline.Contains(pcbnew.VECTOR2I(int(px), int(py))) for px, py in corners):
                continue
            if any(r.Intersects(o) for o in blocked[False]):
                continue
            q = pcbnew.BOX2I(r.GetOrigin(), r.GetSize())
            q.Inflate(MM(0.2))
            blocked[False].append(q)
            placed += 1
            done = True
            break
        if not done:
            ref.SetLayer(pcbnew.F_Fab)
            style(ref, 0.8)
            ref.SetTextThickness(MM(0.12))
            ref.SetPosition(pcbnew.VECTOR2I(int(cx), int(cy)))
            skipped += 1
    return placed, skipped


def main(path, netlist=None):
    b = pcbnew.LoadBoard(path)
    if netlist:
        fields = netlist_fields(netlist)
        for f in b.GetFootprints():
            for name, value in fields.get(f.GetReference(), {}).items():
                if f.HasField(name) and f.GetField(name).GetText() != value:
                    f.GetField(name).SetText(value)
    for f in b.GetFootprints():
        if f.GetReference().startswith('TP'):
            f.SetExcludedFromBOM(False)      # matches the schematic symbols; the BOM export filters on the LCSC field
    for d in list(b.GetDrawings()):
        if d.Type() == pcbnew.PCB_TEXT_T:
            if d.GetLayer() in SILK:
                b.RemoveNative(d)            # labels are regenerated below
                continue
            for k, v in NOTES.items():
                if d.GetText().startswith(k):
                    d.SetText(v)
    # every reference back to the fabrication layer, then promote the ones that fit
    for f in b.GetFootprints():
        r = f.Reference()
        if r.GetLayer() in SILK:
            r.SetLayer(pcbnew.B_Fab if f.IsFlipped() else pcbnew.F_Fab)
            style(r, 0.8)
            r.SetTextThickness(MM(0.12))
        for g in f.GraphicalItems():
            if g.GetLayer() in SILK:
                if g.Type() == pcbnew.PCB_TEXT_T:
                    if g.GetTextHeight() < MM(1.0):
                        style(g, 1.0)
                    elif g.GetTextThickness() < MM(0.15):
                        g.SetTextThickness(MM(0.15))
                elif g.Type() == pcbnew.PCB_SHAPE_T and 0 < g.GetWidth() < MM(0.15):
                    g.SetWidth(MM(0.15))
    for text, x, y, side, size, rot in LABELS:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(text)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.F_SilkS if side == 'F' else pcbnew.B_SilkS)
        style(t, size)
        t.SetTextAngleDegrees(rot)
        if side == 'B':
            t.SetMirrored(True)
        b.Add(t)
    placed, skipped = place_references(b)
    pcbnew.SaveBoard(path, b)
    print('labels', len(LABELS), 'references on silkscreen', placed, 'kept on fabrication layer', skipped)


if __name__ == '__main__':
    main(*sys.argv[1:3])
