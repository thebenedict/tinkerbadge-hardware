#!/usr/bin/env python3
"""Silkscreen and annotation pass after the design-review routing. KiCad Python. Idempotent.

Moves the reference text of the newly added footprints to the fabrication
layer like the rest of the board, adds user-facing labels, and refreshes the
drawing-layer status notes.
"""
import sys

import pcbnew

MM = pcbnew.FromMM
TAG = 'review-2026-11-10'
REV = 'rev 0.2  2026-11-10'

LABELS = [
    # text, x, y, layer, size, rotation
    ('A', 105.6, 142.2, 'F', 1.2, 0),
    ('B', 105.6, 152.2, 'F', 1.2, 0),
    ('USB', 201.0, 119.6, 'F', 1.0, 0),
    ('QWIIC', 203.2, 154.2, 'F', 0.8, 0),
    ('EPD', 201.5, 135.6, 'F', 0.8, 0),
    ('TINKER BADGE', 126.0, 110.6, 'B', 2.0, 0),
    ('AI Tinkerers Seattle', 126.0, 113.6, 'B', 1.0, 0),
    (REV, 126.0, 115.6, 'B', 0.8, 0),
    ('CERN-OHL-P-2.0', 126.0, 117.4, 'B', 0.8, 0),
    ('EN', 174.0, 118.2, 'B', 0.8, 0), ('BOOT', 177.0, 113.8, 'B', 0.8, 0), ('3V3', 180.0, 118.2, 'B', 0.8, 0),
    ('GND', 183.0, 113.8, 'B', 0.8, 0), ('TX', 186.0, 118.2, 'B', 0.8, 0), ('RX', 189.0, 113.8, 'B', 0.8, 0),
    ('BAT +', 174.6, 143.6, 'B', 0.8, 0), ('-', 178.4, 143.6, 'B', 0.8, 0),
    ('1S LiPo 4.2V  CHECK POLARITY', 180.6, 137.0, 'B', 0.8, 90),
    ('DOCK', 124.0, 170.4, 'B', 1.0, 0),
]
NOTES = {
    'EXPERIMENTAL 110 x 80': 'TINKER BADGE 110 x 80 - DESIGN REVIEW 2026-11-10 - PROTOTYPE, VISUAL REVIEW REQUIRED',
    'NFC 18 x 13 RESERVE': 'NFC COIL - REAR',
}


def netlist_fields(path):
    import pathlib
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


def main(path, netlist=None):
    b = pcbnew.LoadBoard(path)
    if netlist:
        fields = netlist_fields(netlist)
        for f in b.GetFootprints():
            for name, value in fields.get(f.GetReference(), {}).items():
                if f.HasField(name) and f.GetField(name).GetText() != value:
                    f.GetField(name).SetText(value)
    for d in list(b.GetDrawings()):
        if d.Type() == pcbnew.PCB_TEXT_T:
            if d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                b.RemoveNative(d)          # labels are regenerated below
                continue
            for k, v in NOTES.items():
                if d.GetText().startswith(k):
                    d.SetText(v)
    for f in b.GetFootprints():
        r = f.Reference()
        if r.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            r.SetLayer(pcbnew.F_Fab if r.GetLayer() == pcbnew.F_SilkS else pcbnew.B_Fab)
            r.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8)))
            r.SetTextThickness(MM(0.12))
    for f in b.GetFootprints():
        for g in f.GraphicalItems():
            if g.Type() == pcbnew.PCB_TEXT_T and g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g.GetTextHeight() < MM(0.8):
                g.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8)))
                g.SetTextThickness(MM(0.12))
                if f.GetReference() == 'J502':      # keep the row labels clear of the socket outline
                    g.SetX(f.GetPosition().x - MM(5.9))
    for text, x, y, side, size, rot in LABELS:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(text)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.F_SilkS if side == 'F' else pcbnew.B_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(max(0.12, size * 0.15)))
        t.SetTextAngleDegrees(rot)
        if side == 'B':
            t.SetMirrored(True)
        b.Add(t)
    pcbnew.SaveBoard(path, b)
    print('labels', len(LABELS))


if __name__ == '__main__':
    main(*sys.argv[1:3])
